"""Conservative discovery. Only documentary review can validate an opportunity."""
import concurrent.futures as futures
import hashlib
import io
import json
import re
import unicodedata
from datetime import datetime, date, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import noticias
from avaliacao import apply_reviews, documentary_status

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ['graduacao','doutorado','idioma','nacionalidade','residencia','autorizacao_profissional','trabalho_do_brasil']

def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(s)).lower() if not unicodedata.combining(c))

def document_hash(text):
    return hashlib.sha256(' '.join(text.split()).encode()).hexdigest()

def canonical(url):
    u=urlsplit(url)
    return urlunsplit((u.scheme.lower(),u.netloc.lower(),u.path.rstrip('/') or '/',urlencode(sorted((k,v) for k,v in parse_qsl(u.query) if not k.startswith('utm_') and k not in ['jobBoardSource','trk','fbclid'])),''))

def load(name, default):
    path=ROOT/name
    return json.loads(path.read_text()) if path.exists() else default

def write(name, obj):
    path=ROOT/name; tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); tmp.replace(path)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.parts=[]; self.current=None; self.ignore=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ['script','style']: self.ignore+=1
        if tag=='a': self.current=[a.get('href',''),'']
    def handle_endtag(self,tag):
        if tag in ['script','style']: self.ignore=max(0,self.ignore-1)
        if tag=='a' and self.current:
            self.links.append(tuple(self.current)); self.current=None
    def handle_data(self,data):
        if self.ignore:return
        self.parts.append(data)
        if self.current:self.current[1]+=data

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; RadarAcademico/2.0)'}),timeout=18) as r:
        final=r.url; raw=r.read(4000001)
        if len(raw)>4000000:raise ValueError('Documento excede 4 MB')
        content=r.headers.get('Content-Type','')
        if 'pdf' in content or raw.startswith(b'%PDF'):
            try:
                from pypdf import PdfReader
                text=' '.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(raw)).pages[:40])
                return final,None,text
            except ImportError:return final,None,'PDF: extração indisponível, revisão documental necessária'
        page=Page();page.feed(raw.decode(r.headers.get_content_charset() or 'utf-8',errors='replace'))
        return final,page,' '.join(page.parts)

def category(title):
    t=norm(title)
    for key,value in [('substitut','Professor substituto'),('visitant','Professor visitante'),('postdoc','Pós-doutorado'),('pos-dout','Pós-doutorado'),('research','Pesquisador'),('pesquisador','Pesquisador'),('efetivo','Professor efetivo')]:
        if key in t:return value
    return 'Docência / pesquisa a confirmar'

def candidate(title):
    t=norm(title)
    return bool(re.search(r'docent|profess|postdoc|pos.doutor|research|pesquisador|fellowship',t)) and bool(re.search(r'edital|selec|concurso|vaga|vacanc|recruit|job|contrat|fellow|postdoc|pos.doutor',t))

def review_state(item,today=None):
    today=today or datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    item.setdefault('verificacao',{})
    for field in FIELDS:item['verificacao'].setdefault(field,{'valor':'Não informado','evidencia':''})
    reviewed=documentary_status(item,today)
    if reviewed:item['status']=reviewed;return item
    deadline=item.get('prazo','')
    valid_date=False
    try:
        d=date.fromisoformat(deadline);valid_date=True
        if d<today:item['status']='Encerrada';return item
    except (ValueError,TypeError):pass
    evidence=item.get('validacao_documental',{})
    required=['prazo','remuneracao']+FIELDS
    complete=all(evidence.get(k,{}).get('evidencia') and evidence.get(k,{}).get('valor') for k in required)
    # Every field must have an explicit decision and quotation, including exemptions.
    validated=complete and evidence.get('revisor') and evidence.get('data') and evidence.get('url_oficial') and valid_date and evidence.get('elegivel_fisioterapia_doutorado') is True and evidence.get('remunerada') is True
    item['status']='Validada' if validated else 'Não verificado'
    return item

def check_institution(inst):
    now=datetime.now(timezone.utc).isoformat(); result={**inst,'ultima_consulta':now,'status':'Falha','candidatos_encontrados':0};items=[]
    try:
        attempts=[]
        for source in [inst['url']]+inst.get('urls_adicionais',[]):
            try:
                final,page,text=fetch(source)
                if page is not None and len(' '.join(text.split()))<300:raise ValueError('Resposta incompleta ou redirecionamento dependente de script')
                attempts.append({'url':source,'status':'HTTP OK'});break
            except Exception as exc:attempts.append({'url':source,'status':'Falha','erro':str(exc)[:200]})
        else:raise RuntimeError('; '.join(a['erro'] for a in attempts))
        result['tentativas']=attempts;result['url_final']=final
        if page is None:result['status']='Revisão documental necessária';return result,items
        if len(' '.join(text.split()))<300:result['limitacao']='Resposta curta ou redirecionamento dependente de script; conteúdo de editais não confirmado.'
        links=[]
        for href,title in page.links:
            url=urljoin(final,href); title=' '.join(title.split())
            host=urlsplit(url).hostname or ''
            allowed=host==urlsplit(final).hostname or host.endswith('.'+(urlsplit(final).hostname or '').removeprefix('www.'))
            if allowed and url.startswith('https://') and (candidate(title) or (re.search(r'/editais-(temporario|efetivo)',url) and 'edital' in norm(title))):links.append((canonical(url),title))
        # Follow up to three recruitment/index pages, including institutional ATS links.
        navigation=[]
        for href,title in page.links:
            target=urljoin(final,href);host=urlsplit(target).hostname or ''
            trusted=host==urlsplit(final).hostname or host.endswith('.gupy.io')
            if trusted and re.search(r'trabalhe|sele[cç][aã]o.docente|edita|concurs|vacanc|career|recruit',norm(title+' '+href)) and target.startswith('https://') and canonical(target)!=canonical(final):
                navigation.append(target)
        for target in list(dict.fromkeys(navigation))[:3]:
            try:
                child_url,child,_=fetch(target)
                if child:
                    for href,title in child.links:
                        url=urljoin(child_url,href);title=' '.join(title.split())
                        if url.startswith('https://') and urlsplit(url).hostname==urlsplit(child_url).hostname and candidate(title):links.append((canonical(url),title))
            except Exception:pass
        links=list(dict(links).items())[:30]
        for url,title in links:
            items.append({'id':'inst-'+hashlib.sha256(url.encode()).hexdigest()[:20],'titulo':title,'instituicao':inst['nome'],'pais':inst['pais'],'url':url,'fonte':'Institucional direta','data_coleta':now[:10],'ultima_deteccao':now,'categoria':category(title),'modalidade':'Não informada','remuneracao':'Não informada','prazo':'','status':'Não verificado','prioridade':'Fisioterapia' if 'fisioterap' in norm(title) else 'Aderência a revisar'})
        # An HTTP 200 is not evidence that a JS job board was parsed successfully.
        result['status']='Consultada: candidatos a revisar' if items else 'Consulta parcial: nenhum link acadêmico extraído'
        result['candidatos_encontrados']=len(items)
        if not items and re.search(r'nenhuma vaga no momento|no vacancies|no current vacancies',norm(text)):
            result['status']='Consultada: portal informa nenhuma vaga'
        if inst.get('limitacao'):result['limitacao']=inst['limitacao']
        result['resumo_sha256']=document_hash(text)
    except Exception as e:result['erro']=str(e)[:240]
    return result,items

def inspect_document(item):
    if item.get('fonte') not in ['Institucional direta','Edital institucional revisado']:return item
    item['consulta_documental_em']=datetime.now(timezone.utc).isoformat()
    try:
        final,page,text=fetch(item['url']);item['url_documento']=final
        item['documento_sha256']=document_hash(text);item['documento_hash_formato']='texto-v1'
        if item.get('documentos_obrigatorios'):
            item['anexos_sha256']={};item['falhas_anexos']=[]
            for attachment in item['documentos_obrigatorios']:
                try:
                    _,_,body=fetch(attachment);item['anexos_sha256'][attachment]=document_hash(body)
                except Exception as exc:item['falhas_anexos'].append({'url':attachment,'erro':str(exc)[:200]})
        patterns={'graduacao':r'gradua|bacharel|bachelor|degree', 'doutorado':r'doutor|doctor|phd|ph.d', 'idioma':r'idioma|ingles|english|espanhol|portugues|language', 'nacionalidade':r'nacionalidade|nationality|citizen', 'residencia':r'residencia|residen|domicilio', 'autorizacao_profissional':r'crefito|conselho profissional|licen[cs]|registration', 'trabalho_do_brasil':r'remoto|remote|brasil|brazil|home office', 'prazo':r'inscric|deadline|closing date', 'remuneracao':r'remunera|salario|salary|stipend|bolsa|r\$|€|£'}
        sentences=re.split(r'[\n.!?;]+',text)
        item['indicios_documentais']={key:[' '.join(t.split())[:450] for t in sentences if re.search(pattern,norm(t))][:3] for key,pattern in patterns.items()}
        # Snippets are leads, never evidence of confirmed eligibility or a parsed deadline.
        item['resultado_documental']='Indícios extraídos; elegibilidade, anexos e retificações exigem revisão'
    except Exception as e:item['resultado_documental']='Falha: '+str(e)[:200]
    return item

def merge(previous, incoming):
    records=list(previous); byurl={canonical(x['url']):x for x in records if x.get('url')}
    for item in incoming:
        key=canonical(item['url'])
        if key in byurl:
            old=byurl[key];old['ultima_deteccao']=item.get('ultima_deteccao',item.get('data_coleta'))
            for field in ['consulta_documental_em','url_documento','documento_sha256','indicios_documentais','resultado_documental','anexos_sha256','falhas_anexos','documento_hash_formato']:
                if field in item:old[field]=item[field]
            continue
        records.append(item);byurl[key]=item
    return [review_state(x) for x in records]

def main():
    previous=load('vagas.json',[])
    if not isinstance(previous,list):raise ValueError('Catálogo inválido. Não será sobrescrito.')
    institutions=load('instituicoes.json',[]);checks=[]; incoming=[]
    with futures.ThreadPoolExecutor(max_workers=6) as pool:
        for check,items in pool.map(check_institution,[x for x in institutions if x.get('enabled')]):checks.append(check);incoming.extend(items)
    news=[]
    queries=noticias.BUSCAS+['professor fisioterapia EAD remoto online híbrido universidade contratação','remote online faculty physical therapy Brazil postdoctoral paid']
    def search(q):
        try:return q,noticias.pesquisar_noticias(q),None
        except Exception as e:return q,[],str(e)[:200]
    with futures.ThreadPoolExecutor(max_workers=4) as pool:
        for q,items,error in pool.map(search,queries):
            news.append({'consulta':q,'erro':error,'resultados':len(items)})
            for a in items:
                title=a.findtext('title') or '';url=a.findtext('link') or ''
                if not noticias.relevante(title) or not url:continue
                incoming.append({'titulo':title,'url':url,'instituicao':a.findtext('source') or 'Não informada','pais':noticias.identificar_pais(title),'categoria':category(title),'fonte':'Google Notícias RSS','data_coleta':datetime.now(timezone.utc).date().isoformat(),'status':'Não verificado'})
    incoming+=load('oportunidades_curadas.json',[])
    reviews=load('revisoes.json',{})
    def inspect_current(item):
        review=reviews.get(item.get('url',''),{})
        # Listings are queried daily. Documents already archived by a dated review
        # need not be repeatedly downloaded as if they were new vacancies.
        if review.get('triagem') in ['Histórico','Fora da prioridade','Fonte de acompanhamento','Não remunerada','Duplicata'] and not review.get('anuncio_verificado'):
            return item
        return inspect_document(item)
    with futures.ThreadPoolExecutor(max_workers=6) as pool:
        incoming=list(pool.map(inspect_current,incoming))
    records=merge(previous,incoming)
    records=apply_reviews(records,load('revisoes.json',{}),norm,datetime.now(ZoneInfo('America/Sao_Paulo')).date())
    records=[review_state(x) for x in records]
    write('vagas.json',records)
    write('monitoramento.json',{'atualizado_em':datetime.now(timezone.utc).isoformat(),'instituicoes':checks,'noticias':news,'total':len(records),'validadas':sum(x['status']=='Validada' for x in records),'encerradas':sum(x['status']=='Encerrada' for x in records),'anuncios_verificados':sum(x['status']=='Anúncio verificado' for x in records),'triagem':{k:sum(x.get('triagem')==k for x in records) for k in sorted(set(x.get('triagem','Candidato') for x in records))},'falhas':sum(x['status']=='Falha' for x in checks)})
    print(f'{len(previous)} anteriores preservados; {len(records)} registros; {len(checks)} instituições consultadas')
    if checks and all(x['status']=='Falha' for x in checks):raise RuntimeError('Todas as fontes institucionais falharam; consulte monitoramento.json')

if __name__=='__main__':main()
