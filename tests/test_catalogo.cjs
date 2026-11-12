const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
(async()=>{
 const elements=new Map();const element=id=>{if(!elements.has(id))elements.set(id,{value:id==='statusfilter'?'priority':'',textContent:'',innerHTML:'',addEventListener(){}});return elements.get(id)};
 const stored={};stored['radar-fisio-v1']=JSON.stringify([{id:'personal-original',url:'https://example.edu/edital',title:'Título anterior',institution:'Universidade',country:'Brasil',favorite:true,stage:'Enviada',notes:'Nota pessoal preservada'}]);
 const data=[{id:'official-1',url:'https://example.edu/edital',titulo:'Título corrigido',instituicao:'Universidade',pais:'Brasil',prazo:'2099-12-31',remuneracao:'R$ 10.000',status:'Anúncio verificado',auditoria:{data:new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())},triagem:'Candidato',elegibilidade:'Condicionada',verificacao:{graduacao:{valor:'Fisioterapia',fonte:'https://example.edu/edital'}}}];
 const context=vm.createContext({document:{getElementById:element,querySelectorAll(){return[]},addEventListener(){}},localStorage:{getItem:k=>stored[k],setItem:(k,v)=>stored[k]=v},URL,Intl,Date,console,setTimeout,fetch:async url=>({ok:true,json:async()=>url.includes('monitoramento')?{atualizado_em:new Date().toISOString(),falhas:0,instituicoes:[]}:data})});
 const html=fs.readFileSync('index.html','utf8');const code=html.split('<script>')[1].split('</script>')[0].replace(/sincronizarVagas\(\);\s*$/,'');vm.runInContext(code,context);await vm.runInContext('sincronizarVagas()',context);
 let jobs=JSON.parse(stored['radar-fisio-v1']);assert.equal(jobs.length,1);assert.equal(jobs[0].id,'personal-original');assert.equal(jobs[0].favorite,true);assert.equal(jobs[0].stage,'Enviada');assert.equal(jobs[0].notes,'Nota pessoal preservada');assert.equal(jobs[0].title,'Título corrigido');assert.equal(jobs[0].salary,'R$ 10.000');assert.equal(jobs[0].verification,'Anúncio verificado');assert.equal(jobs[0].eligibility,'Condicionada');assert.equal(element('nopen').textContent,1);
 data[0].status='Não verificado';await vm.runInContext('sincronizarVagas()',context);assert.equal(element('nopen').textContent,0);assert.ok(element('joblist').innerHTML.includes('Nenhum anúncio'));
 data[0].status='Anúncio verificado';data[0].prazo='2099-99-99';await vm.runInContext('sincronizarVagas()',context);assert.equal(element('nopen').textContent,0);
 data[0].prazo='2099-12-31';data[0].auditoria.data='2020-01-01';await vm.runInContext('sincronizarVagas()',context);assert.equal(element('nopen').textContent,0);assert.equal(JSON.parse(stored['radar-fisio-v1'])[0].verification,'Revisão necessária');
 data[0].prazo='2020-01-01';data[0].status='Anúncio verificado';await vm.runInContext('sincronizarVagas()',context);jobs=JSON.parse(stored['radar-fisio-v1']);assert.equal(jobs[0].verification,'Encerrada');assert.equal(element('nopen').textContent,0);assert.equal(jobs[0].stage,'Enviada');const reviewDate=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
 const make=(name,extra={})=>({id:name,url:'https://example.edu/'+name,titulo:name,instituicao:'Universidade',pais:'Brasil',status:'Não verificado',triagem:'Candidato',...extra});
 data.splice(0,data.length,
  make('CURRENT',{prazo:'2099-12-31',status:'Anúncio verificado',auditoria:{data:reviewDate}}),
  make('OLD_2024',{titulo:'OLD_2024 Edital 2024',data_coleta:reviewDate}),
  make('EXPIRED_2025',{titulo:'EXPIRED_2025 Edital 2025',prazo:'2025-01-01'}),
  make('NEW_UNKNOWN',{data_coleta:reviewDate}),
  make('EXTENDED_2024',{titulo:'EXTENDED_2024 Edital 2024 prorrogado',prazo:'2099-12-31',status:'Anúncio verificado',auditoria:{data:reviewDate}}),
  make('OLD_FUTURE_UNVERIFIED',{titulo:'OLD_FUTURE_UNVERIFIED Edital 2025',prazo:'2099-12-31'}),
  make('RESULT',{prazo:'2099-12-31',status:'Anúncio verificado',auditoria:{data:reviewDate},triagem:'Histórico'})
 );
 await vm.runInContext('sincronizarVagas()',context);
 assert.equal(element('nopen').textContent,2);assert.equal(JSON.parse(stored['radar-fisio-v1']).length,8);
 const currentHtml=element('joblist').innerHTML;
 assert.ok(currentHtml.includes('CURRENT'));assert.ok(currentHtml.includes('EXTENDED_2024'));
 for(const title of ['OLD_2024','EXPIRED_2025','NEW_UNKNOWN','OLD_FUTURE_UNVERIFIED','RESULT'])assert.ok(!currentHtml.includes(title),title+' não pode aparecer entre vigentes');
 for(const title of ['OLD_2024','EXPIRED_2025','RESULT'])assert.ok(element('archivelist').innerHTML.includes(title));
 for(const title of ['NEW_UNKNOWN','OLD_FUTURE_UNVERIFIED'])assert.ok(element('pendinglist').innerHTML.includes(title));
 assert.ok(!element('pendinglist').innerHTML.includes('OLD_2024'));
 for(const filter of ['','priority','favorite','applied','archive','unverified','open']){
  element('statusfilter').value=filter;vm.runInContext('render()',context);
  for(const title of ['OLD_2024','EXPIRED_2025','NEW_UNKNOWN','RESULT'])assert.ok(!element('joblist').innerHTML.includes(title));
 }
 assert.ok(element('applicationlist').innerHTML.includes('Título corrigido'));
 const original=JSON.parse(stored['radar-fisio-v1']).find(j=>j.id==='personal-original');
 assert.equal(original.favorite,true);assert.equal(original.stage,'Enviada');assert.equal(original.notes,'Nota pessoal preservada');
 assert.ok(!html.includes('<option value="archive">'));assert.ok(html.includes('data-tab="archive"'));assert.ok(html.includes('data-tab="pending"'));
 console.log('Separação de vigentes, pendentes e histórico OK: data de coleta não comprova vigência; prorrogação de edital antigo aceita quando verificada; registros e candidaturas preservados.');
 console.log('Integração do catálogo OK: metadados, candidatura, favorita, notas e encerramento.');
})().catch(e=>{console.error(e);process.exitCode=1});
