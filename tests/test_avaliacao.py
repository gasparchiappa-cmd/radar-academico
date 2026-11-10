import sys,unittest
from pathlib import Path
from datetime import date
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from avaliacao import apply_reviews,documentary_status,screen
from atualizar_vagas import norm,review_state
class ReviewTests(unittest.TestCase):
 def test_voluntary(self):self.assertEqual(screen({'titulo':'Seleção Professores Voluntários'},norm)[0],'Não remunerada')
 def test_results(self):self.assertEqual(screen({'titulo':'Resultado final concurso Fisioterapia'},norm)[0],'Histórico')
 def test_portal(self):self.assertEqual(screen({'titulo':'Comissão de Seleção Docente'},norm)[0],'Fonte de acompanhamento')
 def test_irrelevant(self):self.assertEqual(screen({'titulo':'Concurso professor Engenharia Civil'},norm)[0],'Fora da prioridade')
 def test_relevant(self):self.assertEqual(screen({'titulo':'Concurso Fisioterapia'},norm)[0],'Candidato')
 def sample(self):
  r={'data':'2026-11-10','anuncio_verificado':True,'remunerada':True,'url_oficial':'https://a.br/1','verificacao':{k:{'valor':'Explicitamente conferido','fonte':'https://a.br/1'} for k in ['prazo','remuneracao','graduacao','doutorado','idioma','nacionalidade','residencia','autorizacao_profissional','trabalho_do_brasil']}}
  return {'auditoria':r,'prazo':'2026-12-31'}
 def test_verified_ad_not_person(self):self.assertEqual(documentary_status(self.sample(),date(2026,11,10)),'Anúncio verificado')
 def test_review_expiry(self):self.assertEqual(documentary_status(self.sample(),date(2026,11,18)),'Revisão necessária')
 def test_changed_document(self):
  x=self.sample();x['documento_sha256']='changed';x['auditoria']['documento_sha256']='old';self.assertEqual(documentary_status(x,date(2026,11,10)),'Revisão necessária')
 def test_source_failed(self):
  x=self.sample();x['resultado_documental']='Falha: HTTP 503';self.assertEqual(documentary_status(x,date(2026,11,10)),'Revisão necessária')
 def test_changed_attachment(self):
  x=self.sample();x['auditoria']['anexos_sha256']={'https://a.br/retificacao.pdf':'old'};x['anexos_sha256']={'https://a.br/retificacao.pdf':'new'};self.assertEqual(documentary_status(x,date(2026,11,10)),'Revisão necessária')
 def test_old_deadline_invalidated_by_changed_document(self):
  x={'titulo':'Concurso Fisioterapia','url':'https://a.br/1','prazo':'2020-01-01','documento_sha256':'new'};r=apply_reviews([x],{'https://a.br/1':{'prazo':'2020-01-01','documento_sha256':'old'}},norm);self.assertEqual(r[0]['prazo'],'');self.assertEqual(r[0]['triagem'],'Candidato')
 def test_payment_required(self):
  x=self.sample();x['auditoria']['remunerada']=False;self.assertIsNone(documentary_status(x,date(2026,11,10)))
 def test_review_preserves_personal(self):
  x={'titulo':'Concurso Fisioterapia','url':'https://a.br/1','favorite':True,'stage':'Enviada'};r=apply_reviews([x],{'https://a.br/1':{'prazo':'2020-01-01','triagem':'Histórico'}},norm);self.assertTrue(r[0]['favorite']);self.assertEqual(r[0]['stage'],'Enviada');self.assertEqual(review_state(r[0])['status'],'Encerrada')
if __name__=='__main__':unittest.main()
