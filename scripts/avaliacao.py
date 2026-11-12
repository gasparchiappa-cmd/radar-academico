"""Auditable screening and documentary review, separate from personal eligibility."""
import re
from datetime import date, timedelta
from urllib.parse import urlsplit

def screen(item, normalize):
    t=normalize(item.get('titulo',''));u=item.get('url','')
    if item.get('duplicata_de'):return 'Duplicata','Mesmo edital identificado; registro preservado para candidaturas.'
    if re.search(r'voluntari|unpaid|unremunerated',t):return 'Não remunerada','A própria publicação identifica atuação voluntária ou não remunerada.'
    if re.search(r'resultado|homologacao|inscricoes homologadas|candidatos aprovados|^aprovados$|banca examinadora|relatorio da apuracao|classificacao final|conclusao do concurso',t):return 'Histórico','Resultado ou ato de andamento; não é abertura de inscrições.'
    if re.search(r'solicitacoes de vagas|gestao de vagas|procedimentos-para-realizacao|coordenadoria-de-concursos|/prorh/publicacoes',t+' '+u) or t in ['comissao de selecao docente','concurso livre docente','concurso pesquisador','concurso professor doutor','concurso professor titular']:
        return 'Fonte de acompanhamento','Página geral ou procedimento; não representa uma vaga individual.'
    if re.search(r'mestrado em reabilitacao.*recebe inscricoes',t):return 'Fora da prioridade','Ingresso discente, não contratação acadêmica.'
    relevant=re.search(r'fisioterap|physiotherap|physical therap|reabilita|rehabilita|cardi|fisiologia|physiology|saude coletiva|saude publica|bioquimica|public health|clinical|saude|health|biomateriais|regenerativa|psicologia aplicada',t)
    if relevant:return 'Candidato','Área potencialmente pertinente; exige edital, prazo, remuneração e requisitos.'
    if re.search(r'engenharia|direito|matematica|linguistica|comput|eletron|fisica|quimica|pedagogia|agronom|turismo|libras|geometria|ecologia|educacao|servico social',t):
        return 'Fora da prioridade','Área anunciada fora do foco Fisioterapia/reabilitação/cardiometabólico. Não é juízo de impedimento legal.'
    return 'Candidato','Anúncio geral; área e elegibilidade não demonstradas.'

def apply_reviews(records, reviews, normalize, today=None):
    today=today or date.today()
    for item in records:
        item['triagem'],item['motivo_triagem']=screen(item,normalize)
        review=reviews.get(item.get('url',''),{})
        if not review:continue
        # An explicit human/model documentary review is retained as provenance.
        item['auditoria']=review
        if item.get('documento_hash_formato')=='texto-v1' and review.get('documento_sha256') and item.get('documento_sha256') and review['documento_sha256']!=item['documento_sha256']:
            item['auditoria']={**review,'desatualizada':True};item['prazo']='';item['triagem']='Candidato';item['motivo_triagem']='Documento alterado desde a revisão: prazo e requisitos exigem nova conferência.'
            item['remuneracao']='Documento alterado: rever';continue
        for key in ['prazo','remuneracao','modalidade','verificacao','url_oficial','duplicata_de','grupo_edital','elegibilidade','prioridade','tipo_oportunidade']:
            if key in review:item[key]=review[key]
        if review.get('triagem'):item['triagem']=review['triagem']
        if review.get('motivo'):item['motivo_triagem']=review['motivo']
        if item.get('duplicata_de'):item['triagem']='Duplicata'
    return records

def valid_deadline(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):return None
    try:return date.fromisoformat(value)
    except ValueError:return None

def documentary_status(item,today):
    review=item.get('auditoria',{})
    deadline=valid_deadline(item.get('prazo'))
    if deadline and deadline<today:return 'Encerrada'
    if review.get('encerrada_evidencia'):return 'Encerrada'
    if review.get('anuncio_verificado'):
        # Confirmation describes the advertisement, never certifies this user's eligibility.
        try:fresh=date.fromisoformat(review['data'])<=today<=date.fromisoformat(review['data'])+timedelta(days=7)
        except (KeyError,ValueError,TypeError):fresh=False
        changed=review.get('documento_sha256') and item.get('documento_sha256') and review['documento_sha256']!=item['documento_sha256']
        attempted=item.get('resultado_documental','').startswith('Falha:') or bool(item.get('falhas_anexos'))
        for url,digest in review.get('anexos_sha256',{}).items():
            if item.get('anexos_sha256',{}).get(url)!=digest:changed=True
        if not fresh or changed or attempted or review.get('desatualizada') or not deadline:return 'Revisão necessária'
        required=['prazo','remuneracao','graduacao','doutorado','idioma','nacionalidade','residencia','autorizacao_profissional','trabalho_do_brasil']
        complete=all(review.get('verificacao',{}).get(k,{}).get('valor') and review['verificacao'][k].get('fonte') for k in required)
        if complete and review.get('url_oficial') and review.get('remunerada') is True:return 'Anúncio verificado'
    return None
