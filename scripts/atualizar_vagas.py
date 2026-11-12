"""Conservative discovery. Only documentary review can validate an opportunity."""
import concurrent.futures as futures
import copy
import os
import hashlib
import io
import json
import re
import unicodedata
from datetime import datetime, date, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode, unquote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import noticias
from avaliacao import apply_reviews, documentary_status, valid_deadline, screen

ROOT = Path(os.environ.get('RADAR_DATA_DIR',Path(__file__).resolve().parent.parent))
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
        if tag=='a' and not self.ignore: self.current=[a.get('href',''),'']
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
        charset=r.headers.get_content_charset()
        if not charset:
            meta=re.search(br'charset\s*=\s*["\']?([a-zA-Z0-9_-]+)',raw[:8192],re.I)
            charset=meta.group(1).decode('ascii') if meta else 'utf-8'
        try:body=raw.decode(charset,errors='strict')
        except UnicodeDecodeError:body=raw.decode('windows-1252',errors='replace')
        page=Page();page.feed(body)
        return final,page,' '.join(page.parts)

def category(title):
    t=norm(title)
    for key,value in [('substitut','Professor substituto'),('visitant','Professor visitante'),('profix','PROFIX / Fixação de doutores'),('adjunt','Professor adjunto'),('assistente','Professor assistente'),('assistant professor','Professor assistente'),('postdoc','Pós-doutorado'),('pos-dout','Pós-doutorado'),('research','Pesquisador'),('pesquisador','Pesquisador'),('efetivo','Professor efetivo')]:
        if key in t:return value
    return 'Docência / pesquisa a confirmar'

def candidate(title,url=""):
    t=norm(title)
    path=norm(unquote(urlsplit(url).path))
    academic_terms=r'docent|profess|profesor|lecturer|postdoc|pos.doutor|research|pesquisador|investigador|fellowship|profix|fixacao.de.doutores'
    generic=bool(re.fullmatch(r'(edital|baixar|download)(\s+.*)?',t))
    academic=bool(re.search(academic_terms,t)) or (generic and bool(re.search(academic_terms,path.rsplit('/',1)[-1])))
    recruitment=bool(re.search(r'edital|selec|concurso|vaga|vacanc|recruit|job|contrat|fellow|postdoc|pos.doutor|convocatoria|plaza|profix|fixacao.de.doutores',t+' '+path))
    job_page=bool(re.search(r'/jobs/[^/?#]+|/vacanc(?:y|ies)/[^/?#]+',urlsplit(url).path,re.I))
    return academic and (recruitment or job_page)

def review_state(item,today=None):
    today=today or datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    item.setdefault('verificacao',{})
    for field in FIELDS:item['verificacao'].setdefault(field,{'valor':'Não informado','evidencia':''})
    reviewed=documentary_status(item,today)
    if reviewed:item['status']=reviewed;return item
    d=valid_deadline(item.get('prazo'))
    valid_date=d is not None
    if d and d<today:item['status']='Encerrada';return item
    evidence=item.get('validacao_documental',{})
    required=['prazo','remuneracao']+FIELDS
    complete=all(evidence.get(k,{}).get('evidencia') and evidence.get(k,{}).get('valor') for k in required)
    # Every field must have an explicit decision and quotation, including exemptions.
    evidence_date=valid_deadline(evidence.get('data'))
    fresh=evidence_date is not None and 0<=(today-evidence_date).days<=7
    safe=not item.get('resultado_documental','').startswith('Falha:') and not item.get('falhas_anexos')
    unchanged=not evidence.get('documento_sha256') or evidence.get('documento_sha256')==item.get('documento_sha256')
    validated=fresh and safe and unchanged and complete and evidence.get('revisor') and evidence.get('data') and evidence.get('url_oficial') and valid_date and evidence.get('elegivel_fisioterapia_doutorado') is True and evidence.get('remunerada') is True
    item['status']='Validada' if validated else 'Não verificado'
    return item

def trusted_link(url, root, inst):
    """Never trust arbitrary ATS tenants merely because they use the same provider."""
    host=urlsplit(url).hostname or ''
    base=(urlsplit(root).hostname or '').removeprefix('www.')
    return (url.startswith('https://') and
            (host==base or host.endswith('.'+base) or host in inst.get('hosts_adicionais',[])))

def check_institution(inst):
    now=datetime.now(timezone.utc).isoformat()
    result={**inst,'ultima_consulta':now,'status':'Falha','candidatos_encontrados':0,
            'tentativas':[],'paginas_consultadas':0,'falhas_navegacao':0}
    links={};texts=[];visited=set();pending=[];empty=False
    for source in [inst['url']]+inst.get('urls_adicionais',[]):
        if source not in pending:pending.append(source)
    roots=list(pending)
    # Every explicitly configured source is queried. Discovery has a separate bound.
    navigation_budget=3
    while pending:
        source=pending.pop(0)
        if canonical(source) in visited:continue
        visited.add(canonical(source))
        attempt={'url':source,'tipo':'configurada' if source in roots else 'navegacao'}
        result['tentativas'].append(attempt)
        try:
            final,page,text=fetch(source)
            attempt['url_final']=final
            if not any(trusted_link(final,root,inst) for root in roots):
                raise ValueError('Redirecionamento fora dos domínios institucionais autorizados')
            if page is None or len(' '.join(text.split()))<300:
                raise ValueError('Conteúdo insuficiente: PDF, página curta ou dependente de script')
            attempt['status']='HTTP OK';attempt['resumo_sha256']=document_hash(text)
            result['paginas_consultadas']+=1;result.setdefault('url_final',final);texts.append(text)
            empty=empty or bool(re.search(r'nenhuma vaga no momento|no vacancies|no current vacancies',norm(text)))
            navigation=[]
            for href,title in page.links:
                target=urljoin(final,href);title=' '.join(title.split())
                if not any(trusted_link(target,root,inst) for root in roots):continue
                key=canonical(target)
                if candidate(title,target) or (re.search(r'/editais-(temporario|efetivo)',target) and 'edital' in norm(title)):
                    links.setdefault(key,title)
                if (key not in visited and target not in pending and not urlsplit(target).path.lower().endswith('.pdf') and
                    re.search(r'trabalhe|selecao.docente|edita|concurs|vacanc|career|recruit',norm(title+' '+href))):
                    navigation.append(target)
            for target in dict.fromkeys(navigation):
                if navigation_budget<=0:break
                pending.append(target);navigation_budget-=1
        except Exception as exc:
            attempt.update(status='Falha',erro=str(exc)[:240])
            if attempt['tipo']=='navegacao':result['falhas_navegacao']+=1
    all_links=list(links.items())
    result['links_academicos_extraidos']=len(all_links)
    result['limite_candidatos_atingido']=len(all_links)>30
    items=[{'id':'inst-'+hashlib.sha256(url.encode()).hexdigest()[:20],
            'titulo':title,'instituicao':inst['nome'],'pais':inst['pais'],'url':url,
            'fonte':'Institucional direta','data_coleta':now[:10],'ultima_deteccao':now,
            'categoria':category(title),'modalidade':'Não informada','remuneracao':'Não informada',
            'prazo':'','status':'Não verificado',
            'prioridade':'Fisioterapia' if 'fisioterap' in norm(title) else 'Aderência a revisar'}
           for url,title in all_links[:30]]
    result['candidatos_encontrados']=len(items)
    failed=[a for a in result['tentativas'] if a['status']=='Falha']
    if texts:
        result['status']='Consultada: candidatos a revisar' if items else 'Consulta parcial: nenhum link acadêmico extraído'
        if empty and not items:result['status']='Consultada: portal informa nenhuma vaga'
        if failed or result['limite_candidatos_atingido']:
            result['status']='Consulta parcial: candidatos a revisar' if items else 'Consulta parcial: sem cobertura integral'
        result['resumo_sha256']=document_hash(' '.join(texts))
    else:result['erro']='; '.join(a.get('erro','') for a in failed)[:500]
    return result,items

def security_signals(text):
    invisible=sum(unicodedata.category(c)=='Cf' for c in text)
    suspicious=bool(re.search(r'ignore (all |previous )?instructions|system prompt|ignore as instrucoes|reveal.*(secret|token)',norm(text)))
    return {'caracteres_formato':invisible,'instrucao_suspeita':suspicious,
            'tratamento':'Conteúdo externo tratado como dados; nenhuma instrução executada'}

def inspect_document(item):
    if item.get('fonte') not in ['Institucional direta','Edital institucional revisado']:return item
    item['consulta_documental_em']=datetime.now(timezone.utc).isoformat()
    try:
        final,page,text=fetch(item['url']);item['url_documento']=final
        if not text.strip() or text.startswith('PDF: extração indisponível'):raise ValueError('Texto documental indisponível; requer revisão manual/OCR')
        item['seguranca_documental']=security_signals(text)
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
    records=copy.deepcopy(previous); byurl={canonical(x['url']):x for x in records if x.get('url')}
    for item in incoming:
        key=canonical(item['url'])
        if key in byurl:
            old=byurl[key];old['ultima_deteccao']=item.get('ultima_deteccao',item.get('data_coleta'))
            for field in ['consulta_documental_em','url_documento','documento_sha256','indicios_documentais','resultado_documental','anexos_sha256','falhas_anexos','documento_hash_formato','seguranca_documental']:
                if field in item:old[field]=item[field]
            continue
        records.append(item);byurl[key]=item
    return [review_state(x) for x in records]

def assert_preserved(previous, records):
    from collections import Counter
    identity=lambda x:(x.get('id'),x.get('url'))
    if Counter(map(identity,previous))-Counter(map(identity,records)):
        raise ValueError('Registros históricos ausentes; gravação bloqueada')
    old_personal=[{k:x[k] for k in ['favorite','stage','notes'] if k in x} for x in previous]
    if old_personal!=[{k:x[k] for k in ['favorite','stage','notes'] if k in x} for x in records[:len(previous)]]:
        raise ValueError('Dados de candidaturas alterados; gravação bloqueada')

def main():
    previous=load('vagas.json',[])
    if not isinstance(previous,list):raise ValueError('Catálogo inválido. Não será sobrescrito.')
    institutions=load('instituicoes.json',[]);checks=[]; incoming=[]
    if not any(x.get('enabled') for x in institutions):raise ValueError('Nenhuma instituição ativa; gravação bloqueada')
    with futures.ThreadPoolExecutor(max_workers=6) as pool:
        for check,items in pool.map(check_institution,[x for x in institutions if x.get('enabled')]):checks.append(check);incoming.extend(items)
    if all(x['status']=='Falha' for x in checks):
        raise RuntimeError('Todas as fontes institucionais falharam; catálogo e monitoramento anteriores preservados')
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
    incoming_urls={canonical(x['url']) for x in incoming}
    for old in previous:
        if (old.get('auditoria',{}).get('anuncio_verificado') or old.get('validacao_documental')) and canonical(old['url']) not in incoming_urls:
            incoming.append(copy.deepcopy(old))
    reviews=load('revisoes.json',{})
    def inspect_current(item):
        review=reviews.get(item.get('url',''),{})
        # Listings are queried daily. Documents already archived by a dated review
        # need not be repeatedly downloaded as if they were new vacancies.
        triage=review.get('triagem') or screen(item,norm)[0]
        if triage in ['Histórico','Fora da prioridade','Fonte de acompanhamento','Não remunerada','Duplicata'] and not review.get('anuncio_verificado'):
            return item
        return inspect_document(item)
    with futures.ThreadPoolExecutor(max_workers=6) as pool:
        incoming=list(pool.map(inspect_current,incoming))
    records=merge(previous,incoming)
    records=apply_reviews(records,load('revisoes.json',{}),norm,datetime.now(ZoneInfo('America/Sao_Paulo')).date())
    records=[review_state(x) for x in records]
    assert_preserved(previous,records)
    write('vagas.json',records)
    write('monitoramento.json',{'atualizado_em':datetime.now(timezone.utc).isoformat(),'instituicoes':checks,'noticias':news,'total':len(records),'validadas':sum(x['status']=='Validada' for x in records),'encerradas':sum(x['status']=='Encerrada' for x in records),'anuncios_verificados':sum(x['status']=='Anúncio verificado' for x in records),'triagem':{k:sum(x.get('triagem')==k for x in records) for k in sorted(set(x.get('triagem','Candidato') for x in records))},'instituicoes_tentadas':len(checks),'instituicoes_com_leitura':sum(x['paginas_consultadas']>0 for x in checks),'consultas_parciais':sum(x['status'].startswith('Consulta parcial') for x in checks),'candidatos_coletados':len(incoming),'novos_registros':len(records)-len(previous),'falhas':sum(x['status']=='Falha' for x in checks)})
    print(f'{len(previous)} anteriores preservados; {len(records)} registros; {len(checks)} instituições consultadas')


if __name__=='__main__':main()
