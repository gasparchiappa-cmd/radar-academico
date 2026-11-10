# Radar Acadêmico: relatório de entrega e verificação

Data: 10/11/2026. Versão publicada: 2.1.

## Resultado verificado

Site: https://gasparchiappa-cmd.github.io/radar-academico/

A execução [42908938201](https://github.com/gasparchiappa-cmd/radar-academico/actions/runs/42908938201) concluiu com sucesso os testes, coleta, gravação e publicação. O agendamento original permanece diário às 08:00 de Brasília. O agendador do GitHub pode sofrer atrasos; não há garantia de execução no minuto exato.

Última coleta confirmada no site: 10/11/2026 às 18:52:31 de Brasília.

| Verificação | Resultado |
|---|---:|
| Instituições cadastradas | 31 |
| Registros preservados no catálogo | 152 |
| Registros anteriores preservados por URL | 111 de 111 |
| Anúncios remunerados verificados e com prazo aberto | 1 |
| Registros com inscrições encerradas por evidência | 33 |
| Fontes com falha nesta execução | 5 |
| Testes Python | 22 aprovados |
| Teste de integração JavaScript | aprovado |

Os 152 registros NÃO representam 152 vagas abertas, remuneradas ou compatíveis com o usuário. O catálogo também preserva históricos, candidatos, páginas gerais e registros fora da prioridade.

## Alterações realizadas

1. Preservada a interface e a chave local radar-fisio-v1, bem como favoritas, notas e situação das candidaturas. A sincronização atualiza informações do catálogo sem substituir esses campos pessoais. O limite de comprimento de IDs na restauração foi ampliado para evitar colisões entre URLs longas.
2. Mantido o Google Notícias como descoberta complementar. As notícias não são promovidas automaticamente a vagas confirmadas.
3. Incluída consulta direta às 11 instituições solicitadas e expansão para outras instituições do RS, nacionais e internacionais. O cadastro passou de 24 para 31 fontes, incluindo UFCSPA, UNIFESP, UNIFAL-MG, UFG, UDESC, UFJF e UNINTER.
4. Corrigidas páginas de consulta de URI, Ulbra, UnB, Feevale, Universidade do Porto e Melbourne. A resolução de uma URL não garante acesso integral ao portal; limitações são explicitadas abaixo.
5. Criada a triagem por finalidade: candidato, histórico, fora da prioridade, fonte de acompanhamento, duplicata e atuação não remunerada. A classificação de área é uma triagem de prioridade, não uma conclusão legal de inabilitação.
6. Registradas 113 revisões e decisões iniciais em revisoes.json, incluindo os 111 registros anteriores e dois anúncios oficiais adicionais. Novos links recebidos pela rotina passam por triagem conservadora e permanecem não verificados quando faltam provas.
7. Documentados prazos de editais antigos, incluindo UCPel/Fisioterapia/Terapia Intensiva, encerrado em 08/11/2025, e o edital UFG 22/2024. A notícia repetida do mesmo edital da UFG foi vinculada como duplicata, sem apagar seus dados.
8. A lista principal exibe anúncios verificados abertos. Candidatos e histórico têm filtros separados. A aba Instituições Monitoradas informa data, fonte, falhas e consultas parciais.
9. Acrescentados campos documentais de graduação, doutorado, remuneração, prazo, idioma, nacionalidade, residência, autorização profissional e possibilidade de trabalhar do Brasil, com fonte e ressalvas.
10. Acrescentada revalidação conservadora: confirmação positiva expira em sete dias; alteração detectada de documento ou falha na consulta suspende a confirmação. No anúncio UFCSPA são conferidos também edital, anexos e retificação. As assinaturas do texto normalizam espaços e quebras de linha para evitar falsas mudanças.
11. A rotina diária executa os testes antes da coleta. A publicação solicita a compilação da fonte Pages existente e verifica o commit publicado, evitando o conflito inicial entre duas formas de deploy. Execuções substituídas por uma revisão mais nova são canceladas.

## Oportunidades revistas em detalhe

### UNIFESP, edital 755/2026

Anúncio remunerado verificado no documento oficial: professor substituto em Fisioterapia/Saúde da Mulher, Campus Baixada Santista, 40h, contrato de até seis meses. Inscrições até 12/11/2026. Remuneração publicada: R$ 6.157,29 brutos/mês e auxílio-alimentação de R$ 1.192,00. Exige graduação em Fisioterapia e mestrado em Ciências da Saúde. O doutorado não foi tratado como substituto automático do mestrado exigido. A elegibilidade pessoal e o domínio da subárea precisam de comprovação; o anúncio não é remoto.

Fonte: https://phpu.unifesp.br/concurso/inscricao/editais/edital755-2026.htm

### UFCSPA, edital 118/2026

Foram lidos edital, anexos e retificação. As áreas de Fisioterapia Comunitária e Fisiologia Humana têm uma vaga cada; inscrições de 03 a 17/11/2026. A retificação altera Fisioterapia para 40h com dedicação exclusiva. A remuneração para doutorado nesse regime é R$ 13.753,96 brutos/mês. Fisioterapia exige CREFITO e doutorado em uma das áreas expressamente listadas; Fisiologia admite Fisiologia, Biociências ou Ciências da Saúde. A equivalência formal de Ciências Cardiovasculares não foi presumida.

Na execução automática final, a consulta aos três PDFs excedeu o tempo de acesso. Por isso, o registro está em Revisão necessária e não foi contado como anúncio automaticamente confirmado, apesar da leitura documental local concluída nesta sessão. Isso é um comportamento intencional de segurança contra confirmação sem fonte acessível.

Fonte e anexos: https://ufcspa.edu.br/trabalhe-na-ufcspa/docentes/7872-edital-118-2026-progesp

### CESUCA, seleção 2027/1

O edital atual inclui Fisiologia em Biomedicina e admite graduação na área ou afins, com mestrado ou doutorado. O prazo é 15/11/2026. Não foi presumida a aceitação de Fisioterapia como área afim. O salário não está divulgado, há cadastro de reserva e o registro permanece candidato, não vaga remunerada confirmada.

Fonte: https://cesuca.gupy.io/jobs/12823696

## Cobertura e limitações externas

| Instituição com falha | Evidência desta execução |
|---|---|
| UFRGS | <urlopen error [Errno 101] Network is unreachable> |
| UFPel | Resposta incompleta ou redirecionamento dependente de script |
| UFMG | <urlopen error [SSL: TLSV1_ALERT_INTERNAL_ERROR] tlsv1 alert internal error (_ssl.c:1011)> |
| University of Melbourne | HTTP Error 403: Forbidden; HTTP Error 403: Forbidden |
| UNIFESP | Resposta incompleta ou redirecionamento dependente de script |

Fontes com consulta parcial: UCS, Feevale, FURG, USP, University of Nottingham, UFG, UDESC, UNINTER. Na UCS, a página pública localizada é direcionada a pessoal técnico-administrativo; cobertura docente integral não foi demonstrada. Não é correto interpretar qualquer falha ou consulta parcial como ausência de vagas.

Essas limitações permanecem reais e não foram ocultadas nem contornadas desativando verificações de segurança. Portanto, não há cobertura integral comprovada de todas as instituições solicitadas. A configuração e o monitoramento técnico estão entregues; a validação documental de todos os candidatos e a recuperação de fontes externas inacessíveis NÃO estão concluídas.

Também não há vaga remota confirmada como executável do Brasil nesta entrega. EAD, inscrição online e regime de trabalho remoto são conceitos separados. Novos candidatos, editais e retificações continuarão exigindo análise; o sistema não é um serviço autônomo de adjudicação documental completa.

A deduplicação automática é por URL canônica, complementada por reconciliações documentais registradas. Não se afirma que todas as notícias com URLs diferentes da mesma seleção tenham sido reconciliadas. Nenhum registro anterior foi eliminado para reduzir a contagem. PDFs escaneados sem texto ainda exigem OCR ou revisão manual. Nenhuma candidatura foi enviada.

## Testes e publicação

- 22 testes Python aprovados, incluindo prazo vencido, dados ausentes, atualização de documento/anexo, expiração da revisão, proibição de confirmação sem remuneração e preservação de candidaturas.
- Teste de integração JavaScript aprovado: atualização de título/salário sem perda de ID, favorita, etapa ou nota; vaga vencida deixa de ser contada como aberta.
- Compilação Python e sintaxe JavaScript aprovadas.
- No site público, confirmados sincronização de 152 registros, anúncio UNIFESP na lista principal, 33 encerrados no filtro e o edital UCPel de Terapia Intensiva com prazo de 2025. Conferida a aba institucional e a indicação de cinco falhas.
- Comparação do catálogo anterior com o atual: 111 de 111 URLs preservadas. Os testes de interface anteriores também comprovaram persistência após recarga; os marcadores de teste foram revertidos.

## Arquivos e evidências

- [index.html](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/index.html)
- [scripts/atualizar_vagas.py](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/scripts/atualizar_vagas.py)
- [scripts/avaliacao.py](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/scripts/avaliacao.py)
- [scripts/noticias.py](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/scripts/noticias.py)
- [scripts/publicar_pages.py](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/scripts/publicar_pages.py)
- [instituicoes.json](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/instituicoes.json)
- [revisoes.json](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/revisoes.json)
- [oportunidades_curadas.json](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/oportunidades_curadas.json)
- [monitoramento.json](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/monitoramento.json)
- [vagas.json](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/vagas.json)
- [tests/test_radar.py](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/tests/test_radar.py)
- [tests/test_avaliacao.py](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/tests/test_avaliacao.py)
- [tests/test_catalogo.cjs](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/tests/test_catalogo.cjs)
- [.github/workflows/atualizar-vagas.yml](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/.github/workflows/atualizar-vagas.yml)
- [README.md](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/README.md)
