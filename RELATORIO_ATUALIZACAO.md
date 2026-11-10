# Atualização do Radar Acadêmico, 10/11/2026

## Auditoria

A versão anterior consultava apenas RSS do Google, classificava todos os novos registros como pesquisador e importava somente URLs novas. Correções de prazo e status não chegavam aos registros locais. A interface informava, incorretamente, que não existia sincronização automática. Não havia auditoria institucional nem validação documental.

## Alterações

Cadastro inicial de 24 instituições, incluindo as 11 solicitadas, outras cinco do RS, quatro fontes nacionais e quatro internacionais. Consulta direta de páginas institucionais, navegação limitada em páginas de recrutamento e captura de indícios documentais. RSS complementar mantido e ampliado com consultas remotas. Classificação por título é provisória. Campos ausentes não são inferidos. Separação por filtros de candidatos, validadas e encerradas. Aba Instituições Monitoradas com data, fonte e status. URLs canônicas, histórico e dados anteriores preservados. Sincronização de metadados atualiza registros sem sobrescrever favoritas, etapas ou notas locais. Exportação/importação preservada.

## Verificações

Oito testes unitários passaram na implementação inicial: rastreamento em URLs, preservação de candidatura/campos adicionais, prazo vencido, evidência incompleta, data inválida, prazo desconhecido, descoberta e leitura HTML sem scripts. Compilação Python e sintaxe JavaScript passaram. A primeira coleta preservou os 18 registros anteriores e gerou 90 registros candidatos; esse número não representa vagas confirmadas. A coleta inclui editais gerais e possíveis áreas incompatíveis, que precisam de revisão.

## Limitações explícitas

A coleta não valida automaticamente os requisitos de cada edital. A leitura de anexos, verificação de remuneração, regras migratórias e autorização para trabalho remoto a partir do Brasil dependem de evidência individual. Documentos escaneados não passam por OCR nesta versão. Páginas JS e fontes sem links extraíveis são sinalizadas como parciais. Há erros HTTP externos, registrados por instituição. A deduplicação entre diferentes notícias e o mesmo edital ainda exige revisão. A cobertura internacional é inicial. Nenhuma candidatura é enviada automaticamente.

## Arquivos

`index.html`, `scripts/atualizar_vagas.py`, `scripts/noticias.py`, `instituicoes.json`, `monitoramento.json`, `vagas.json`, `.github/workflows/atualizar-vagas.yml`, `tests/test_radar.py`, `README.md`, `.gitignore`.

## Publicação verificada

Após a liberação da integração, as alterações foram gravadas no repositório. O conflito inicial entre a publicação por artefato e a fonte antiga do Pages foi resolvido mantendo a fonte existente e solicitando explicitamente sua compilação por API. O script scripts/publicar_pages.py verifica que o Pages publicou o commit esperado.

Execução completa aprovada: [GitHub Actions 42876347695](https://github.com/gasparchiappa-cmd/radar-academico/actions/runs/42876347695), com os jobs atualizar e publicar concluídos com sucesso. [Publicação Pages](https://github.com/gasparchiappa-cmd/radar-academico/actions/runs/42876618680) também concluída com sucesso. O agendamento original de 08:00 de Brasília foi mantido; a execução de teste foi acionada antes do próximo horário diário. Isso comprova o fluxo executado, não garante pontualidade futura do agendador.

Verificação direta do site público retornou HTTP 200 para index.html, vagas.json e monitoramento.json. A interface apresenta versão 2.0 e a aba Instituições Monitoradas. O catálogo público contém 111 candidatos e coincide com o relatório da coleta de 10/11/2026 às 15:34:36 de Brasília. Foram consultadas 24 instituições; seis apresentaram falhas nesta execução. Nenhum registro está validado documentalmente, nem foi marcado como encerrado com prazo comprovado.

Na interface pública, foram testados a aba institucional, os filtros de candidatos e validadas e a persistência de favoritas e situação de candidatura após recarregar. Os marcadores criados para o teste foram revertidos. Os oito testes unitários passaram localmente e no GitHub Actions; também passaram a compilação Python e a sintaxe JavaScript.

## Escopo concluído e pendências

A infraestrutura de coleta diária e publicação está em funcionamento e foi verificada. A avaliação documental individual de todos os candidatos ainda NÃO está concluída. Não se deve interpretar os 111 candidatos como 111 vagas remuneradas, abertas ou elegíveis para o usuário. Ainda há fontes com consulta parcial ou falha, e a cobertura nacional/internacional permanece inicial. O filtro de encerradas depende de prazos documentados; a ausência de data não indica vaga aberta.

Campos e regras de validação foram implementados, mas os requisitos individuais de graduação, doutorado, remuneração, idioma, nacionalidade, residência, autorização profissional e trabalho remoto a partir do Brasil continuam pendentes nos candidatos sem prova suficiente. A deduplicação entre URLs distintas da mesma seleção e a leitura exaustiva dos anexos também não estão concluídas. Assim, a publicação foi concluída, mas a solicitação integral de monitoramento com oportunidades documentalmente verificadas ainda tem essas pendências.

## Links dos arquivos modificados

- [Interface e sincronização](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/index.html)
- [Coletor institucional e regras](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/scripts/atualizar_vagas.py)
- [Google Notícias complementar](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/scripts/noticias.py)
- [Publicação e verificação do Pages](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/scripts/publicar_pages.py)
- [Instituições cadastradas](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/instituicoes.json)
- [Auditoria da última coleta](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/monitoramento.json)
- [Catálogo preservado](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/vagas.json)
- [Rotina diária](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/.github/workflows/atualizar-vagas.yml)
- [Testes](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/tests/test_radar.py)
- [Documentação](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/README.md)
- [Exclusões de arquivos temporários](https://github.com/gasparchiappa-cmd/radar-academico/blob/main/.gitignore)
