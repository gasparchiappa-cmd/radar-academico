import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from avaliacao import profile_exclusion,apply_reviews,screen
from atualizar_vagas import norm,category,candidate
from noticias import relevante
class ProfileTests(unittest.TestCase):
 def test_shared_cases(self):
  for c in json.loads((Path(__file__).parent/'perfil_casos.json').read_text()):
   with self.subTest(c['name']):
    item={'titulo':c['title'],'categoria':c.get('category',''),'verificacao':{'graduacao':{'valor':c.get('degree','')}}}
    self.assertEqual(bool(profile_exclusion(item,norm)),c['excluded'])
 def test_old_review_cannot_restore_exclusion(self):
  item={'titulo':'Professor substituto Fisioterapia','url':'https://example.edu/1','stage':'Enviada','favorite':True,'notes':'Preservar'}
  result=apply_reviews([copy.deepcopy(item)],{item['url']:{'triagem':'Candidato','motivo':'Revisão anterior'}},norm)[0]
  self.assertEqual(result['triagem'],'Fora da prioridade')
  for k in ['stage','favorite','notes']:self.assertEqual(result[k],item[k])
 def test_stale_review_cannot_restore_exclusion(self):
  item={'titulo':'Professor substituto Fisioterapia','url':'https://example.edu/1','documento_hash_formato':'texto-v1','documento_sha256':'new'}
  result=apply_reviews([item],{item['url']:{'triagem':'Candidato','documento_sha256':'old'}},norm)[0]
  self.assertEqual(result['triagem'],'Fora da prioridade')
 def test_degree_from_review_controls_profile(self):
  item={'titulo':'Professor Ciências da Saúde','url':'https://example.edu/1'}
  result=apply_reviews([item],{item['url']:{'triagem':'Candidato','verificacao':{'graduacao':{'valor':'Graduação em Medicina','fonte':item['url']}}}},norm)[0]
  self.assertEqual(result['triagem'],'Fora da prioridade')
 def test_desired_categories(self):
  for title,expected in [('Professor Adjunto Fisioterapia','Professor adjunto'),('Professor Assistente Fisioterapia','Professor assistente'),('Professor Visitante Fisioterapia','Professor visitante'),('Edital PROFIX-CB','PROFIX / Fixação de doutores')]:
   self.assertEqual(category(title),expected)
 def test_profix_discovery_without_professor_word(self):
  self.assertTrue(candidate('Edital PROFIX-CB'))
  self.assertTrue(relevante('Edital PROFIX-CB Fixação de Doutores'))
  self.assertEqual(screen({'titulo':'Edital PROFIX-CB'},norm)[0],'Candidato')
 def test_new_policy_does_not_delete_catalog(self):
  root=Path(__file__).resolve().parents[1];original=json.loads((root/'vagas.json').read_text());records=copy.deepcopy(original)
  result=apply_reviews(records,json.loads((root/'revisoes.json').read_text()),norm)
  self.assertEqual([(x.get('id'),x['url']) for x in result],[(x.get('id'),x['url']) for x in original])
  for item in result:
   if profile_exclusion(item,norm):self.assertEqual(item['triagem'],'Fora da prioridade')
if __name__=='__main__':unittest.main()
