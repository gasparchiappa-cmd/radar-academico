import sys,unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from atualizar_vagas import canonical,merge,review_state,candidate,Page,document_hash
class RadarTests(unittest.TestCase):
    def test_hash_line_endings(self):self.assertEqual(document_hash("edital\r\n prazo"),document_hash("edital\n  prazo"))
    def test_tracking(self):self.assertEqual(canonical('https://a.br/job/1?utm_source=x#x'),'https://a.br/job/1')
    def test_preserve_application(self):
        old={'url':'https://a.br/1','favorite':True,'stage':'Enviada','custom':'keep'}
        r=merge([old],[{'url':'https://a.br/1?utm_source=x'}]);self.assertEqual(len(r),1);self.assertEqual(r[0]['stage'],'Enviada');self.assertEqual(r[0]['custom'],'keep')
    def test_expired(self):self.assertEqual(review_state({'prazo':'2020-01-01'},date(2026,11,10))['status'],'Encerrada')
    def test_missing_evidence(self):self.assertEqual(review_state({'status':'Validada','prazo':'2027-01-01'})['status'],'Não verificado')
    def test_invalid_date(self):self.assertEqual(review_state({'prazo':'2026-99-99'})['status'],'Não verificado')
    def test_unknown_deadline(self):self.assertEqual(review_state({})['status'],'Não verificado')
    def test_discovery(self):self.assertTrue(candidate('Edital seleção docente Fisioterapia'));self.assertFalse(candidate('Inscrições vestibular Fisioterapia'))
    def test_html(self):
        p=Page();p.feed('<script>secret</script><a href="/a">Edital docente</a>');self.assertEqual(p.links,[('/a','Edital docente')]);self.assertNotIn('secret',p.parts)
if __name__=='__main__':unittest.main()
