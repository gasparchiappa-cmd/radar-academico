const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
(async()=>{
 const elements=new Map();const element=id=>{if(!elements.has(id))elements.set(id,{value:id==='statusfilter'?'priority':'',textContent:'',innerHTML:'',listeners:{},addEventListener(type,handler){this.listeners[type]=handler}});return elements.get(id)};
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
 const profileCases=JSON.parse(fs.readFileSync('tests/perfil_casos.json','utf8'));
 for(const sample of profileCases){
  context.profileSample={title:sample.title,type:sample.category||'',degreeRequirement:sample.degree||'',triage:'Candidato',deadline:'2099-12-31',verification:'Anúncio verificado',auditDate:reviewDate};
  assert.equal(vm.runInContext('!!profileExclusion(profileSample)',context),sample.excluded,sample.name);
  if(sample.excluded){
   assert.equal(vm.runInContext('isCurrent(profileSample)',context),false,sample.name+' fora de Vigentes');
   assert.ok(vm.runInContext('archiveReason(profileSample)',context),sample.name+' fora de A verificar');
  }
 }
 data.push(make('MEDICAL_ROLE',{titulo:'Professor de Medicina Cirurgia',prazo:'2099-12-31',status:'Anúncio verificado',auditoria:{data:reviewDate}}),make('SUBSTITUTE_ROLE',{titulo:'Professor Substituto Fisioterapia',prazo:'2099-12-31',status:'Anúncio verificado',auditoria:{data:reviewDate}}));
 element('statusfilter').value='priority';await vm.runInContext('sincronizarVagas()',context);
 assert.equal(element('nopen').textContent,2);
 for(const title of ['Professor de Medicina Cirurgia','Professor Substituto Fisioterapia']){
  assert.ok(!element('joblist').innerHTML.includes(title));assert.ok(!element('pendinglist').innerHTML.includes(title));assert.ok(element('archivelist').innerHTML.includes(title));
 }
 assert.equal(JSON.parse(stored['radar-fisio-v1']).length,10);
 const expectedUFs={AC:'Norte',AL:'Nordeste',AP:'Norte',AM:'Norte',BA:'Nordeste',CE:'Nordeste',DF:'Centro-Oeste',ES:'Sudeste',GO:'Centro-Oeste',MA:'Nordeste',MT:'Centro-Oeste',MS:'Centro-Oeste',MG:'Sudeste',PA:'Norte',PB:'Nordeste',PR:'Sul',PE:'Nordeste',PI:'Nordeste',RJ:'Sudeste',RN:'Nordeste',RS:'Sul',RO:'Norte',RR:'Norte',SC:'Sul',SP:'Sudeste',SE:'Nordeste',TO:'Norte'};
 for(const [uf,region] of Object.entries(expectedUFs)){
  context.regionSample={country:'Brasil',stateCode:uf};assert.equal(vm.runInContext('jobRegions(regionSample)[0]',context),region,uf);
 }
 const regionalCases=[
  [{country:'Brasil',title:'Professor de Fisioterapia - RS'},['Sul']],
  [{country:'Brasil',title:'Professor - RSBanco de talentos'},['Sul']],
  [{country:'Brasil',workStates:['PR','SP']},['Sul','Sudeste']],
  [{country:'Brasil',workStates:['Espírito Santo']},['Sudeste']],
  [{country:'Brasil',title:'Professor UFRGS',institution:'Universidade Federal do Rio Grande do Sul'},['unknown']],
  [{country:'Brasil',title:'Professor UFAM',institution:'Universidade Federal do Amazonas',mode:'Remoto/EAD'},['unknown']],
  [{country:'Portugal',title:'Professor - SP',workStates:['SP']},['exterior']],
  [{country:'Não informado',title:'Professor - PA'},['unknown']]
 ];
 for(const [sample,expected] of regionalCases){context.regionSample=sample;assert.deepEqual(Array.from(vm.runInContext('jobRegions(regionSample)',context)),expected)}
 const verified={status:'Anúncio verificado',prazo:'2099-12-31',auditoria:{data:reviewDate}};
 for(const [name,uf] of [['SUL','RS'],['SUDESTE','SP'],['CENTRO','DF'],['NORTE','AM'],['NORDESTE','BA']])data.push(make('REGION_'+name,{...verified,uf}));
 data.push(make('REGION_MULTI',{...verified,ufs:['SC','ES']}),make('REGION_EXTERIOR',{...verified,pais:'Portugal'}),make('REGION_UNKNOWN',{...verified}),make('PENDING_SUL',{uf:'RS'}),make('ARCHIVED_SUL',{uf:'RS',prazo:'2020-01-01'}));
 await vm.runInContext('sincronizarVagas()',context);
 const totalBeforeFilter=JSON.parse(stored['radar-fisio-v1']).length;
 for(const [region,shown,other] of [['Sul','REGION_SUL','REGION_SUDESTE'],['Sudeste','REGION_SUDESTE','REGION_SUL'],['Centro-Oeste','REGION_CENTRO','REGION_NORTE'],['Norte','REGION_NORTE','REGION_NORDESTE'],['Nordeste','REGION_NORDESTE','REGION_SUL']]){
  element('region').value=region;vm.runInContext('render()',context);assert.ok(element('joblist').innerHTML.includes(shown),region);assert.ok(!element('joblist').innerHTML.includes(other),region);
  assert.ok(!element('joblist').innerHTML.includes('REGION_EXTERIOR'));assert.ok(!element('joblist').innerHTML.includes('REGION_UNKNOWN'));
 }
 element('region').value='Sul';vm.runInContext('render()',context);assert.equal(element('nopen').textContent,2);assert.ok(element('joblist').innerHTML.includes('REGION_MULTI'));assert.ok(element('pendinglist').innerHTML.includes('PENDING_SUL'));assert.ok(element('archivelist').innerHTML.includes('ARCHIVED_SUL'));
 vm.runInContext("jobs.find(j=>j.title==='REGION_SUL').stage='Enviada';save()",context);assert.ok(element('applicationlist').innerHTML.includes('REGION_SUL'));
 element('region').value='Sudeste';vm.runInContext('render()',context);assert.ok(!element('applicationlist').innerHTML.includes('REGION_SUL'));
 element('region').value='unknown';vm.runInContext('render()',context);assert.ok(element('joblist').innerHTML.includes('REGION_UNKNOWN'));assert.ok(!element('joblist').innerHTML.includes('REGION_SUL'));
 element('region').value='exterior';vm.runInContext('render()',context);assert.ok(element('joblist').innerHTML.includes('REGION_EXTERIOR'));assert.ok(!element('joblist').innerHTML.includes('REGION_SUL'));
 element('clearregion').listeners.click();assert.equal(element('region').value,'');assert.ok(element('joblist').innerHTML.includes('REGION_SUL'));assert.ok(element('joblist').innerHTML.includes('REGION_EXTERIOR'));
 assert.equal(JSON.parse(stored['radar-fisio-v1']).length,totalBeforeFilter);
 assert.equal(JSON.parse(stored['radar-fisio-v1']).find(j=>j.id==='personal-original').notes,'Nota pessoal preservada');
 assert.equal(JSON.parse(stored['radar-fisio-v1']).find(j=>j.title==='REGION_SUL').stage,'Enviada');
 console.log('Filtro regional OK: 27 UFs, cinco regiões, exterior, local desconhecido, múltiplas regiões, quatro abas, limpar filtro e preservação de candidaturas.');
 console.log('Perfil Fisioterapia OK: Medicina e substitutos fora das listas de interesse; visitantes, adjuntos, assistentes e PROFIX preservados; histórico e candidaturas intactos.');
 console.log('Separação de vigentes, pendentes e histórico OK: data de coleta não comprova vigência; prorrogação de edital antigo aceita quando verificada; registros e candidaturas preservados.');
 console.log('Integração do catálogo OK: metadados, candidatura, favorita, notas e encerramento.');
})().catch(e=>{console.error(e);process.exitCode=1});
