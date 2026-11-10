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

Publicação bloqueada. A integração GitHub recusou criação de árvore e criação de arquivo simples com HTTP 403, Resource not accessible by integration. Nenhum arquivo remoto foi alterado. A instalação identificada é https://github.com/settings/installations/180518311 e usa seleção de repositórios. O site público foi aberto e ainda exibe a versão 1.0 e os 18 registros antigos. O workflow revisado ainda não foi executado no GitHub e a publicação não foi validada. O trabalho está em andamento, pendente de autorização da integração para gravar neste repositório e nos workflows.
