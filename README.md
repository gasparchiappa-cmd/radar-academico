# Radar Acadêmico

Monitoramento diário de oportunidades acadêmicas, com prioridade a graduados em Fisioterapia com doutorado.

## Funcionamento

- `instituicoes.json`: fontes institucionais configuráveis, com 17 instituições do RS e expansão inicial nacional e internacional.
- `scripts/atualizar_vagas.py`: consulta direta, navegação limitada a três páginas de recrutamento por instituição, leitura dos candidatos, deduplicação de URLs e auditoria da execução.
- `scripts/noticias.py`: consultas complementares ao Google Notícias, incluindo trabalho remoto.
- `vagas.json`: histórico preservado. Candidatos não são vagas confirmadas.
- `monitoramento.json`: última tentativa de consulta, falhas, consultas parciais e contagens.
- `index.html`: catálogo sincronizado e controle local de candidaturas. A chave `radar-fisio-v1` foi preservada.

## Evidência e validação

A extração de indícios não confirma elegibilidade. Cada registro contém campos para graduação, doutorado, idioma, nacionalidade, residência, autorização profissional e trabalho a partir do Brasil. Prazos, remuneração e requisitos desconhecidos permanecem não informados. Cadastro reserva não garante contratação.

A regra legada `Validada` foi preservada para compatibilidade. Uma oportunidade somente recebe `Validada` quando `validacao_documental` contém revisor, data, URL oficial, decisões explícitas de elegibilidade para Fisioterapia/doutorado e de remuneração, e `valor` e `evidencia` para todos os requisitos, prazo e remuneração. Evidências devem ser trechos do edital ou anexos, inclusive quando documentarem isenção ou ausência de exigência. O prazo ISO deve ser confirmado em `prazo`. Não preencha com inferências. Validação exige revisão de anexos e retificações. Prazo anterior à data de Brasília resulta em `Encerrada`; prazo ausente nunca significa aberta.

Os indícios documentais são armazenados em `indicios_documentais`, junto com URL, data e hash do texto. PDFs precisam de `pypdf`; PDF escaneado requer OCR/manual. Não são executados scripts, macros ou instruções dos documentos. Não há detector de marca d'água estatística.

## Atualização e publicação

A rotina existente das 11:00 UTC (08:00 Brasília) foi mantida, com execução manual e execução após mudanças no código. O workflow executa testes, coleta, salva os dados e publica explicitamente no Pages, evitando depender de um push do bot para iniciar outro workflow. A programação do GitHub pode sofrer atrasos. Falha global institucional encerra o job com erro e impede publicação de uma execução aparentemente bem-sucedida.

## Testes locais

```sh
python -m unittest discover -s tests -v
python scripts/atualizar_vagas.py
```

## Limitações

Não há cobertura exaustiva de universidades, departamentos ou anexos. A expansão ocorre adicionando fontes ao cadastro, não por descoberta autônoma irrestrita. Páginas dinâmicas, login, bloqueios, paginação e links sem título podem escapar. Uma consulta parcial nunca prova ausência de vagas. Deduplicação canônica elimina variantes de rastreamento; notícias e editais com URLs diferentes podem representar a mesma seleção e exigem reconciliação documental. Registros antigos não são apagados. Favoritas, etapas e notas pessoais ficam no navegador; exporte backups periódicos.

## Revisão documental e triagem 2.1

`revisoes.json` registra decisões sobre os registros anteriores, motivos, fontes e prazos documentados. `oportunidades_curadas.json` acrescenta anúncios oficiais conferidos. `scripts/avaliacao.py` distingue candidato, histórico, fora da prioridade, página de acompanhamento, duplicata e atuação não remunerada. O catálogo original nunca é apagado. Anúncios verificados abertos aparecem primeiro; candidatos e histórico possuem filtros próprios.

`Anúncio verificado` confirma a existência e os dados publicados de uma seleção remunerada com prazo, não certifica a elegibilidade pessoal. Requisitos ausentes são explicitamente descritos como não especificados e não se tornam dispensas. Diploma, mestrado, registro profissional e subárea precisam de comprovação. A seleção UFCSPA exige conferir a equivalência formal da área do doutorado; UNIFESP exige mestrado na área indicada. Cadastro de reserva e salário não divulgado não são promovidos a vaga remunerada confirmada.

Revisões positivas expiram após sete dias e perdem confirmação se o texto oficial consultado mudar ou sua consulta falhar. A fonte completa, anexos e retificações estão indicados nos registros curados. No anúncio UFCSPA também são comparados os hashes do edital, anexos e retificação. Demais páginas sem manifesto de anexos ainda exigem conferência dos anexos antes da inscrição. Nenhum anúncio remoto é marcado como acessível do Brasil apenas por oferecer inscrição online ou ensino EAD.

Há 22 testes Python e um teste de integração JavaScript que verifica atualização de metadados e preservação de candidatura, favorita e notas, além do encerramento de prazo.

As páginas de instituições são consultadas diariamente. Documentos já classificados como históricos, fontes gerais ou fora da prioridade não são novamente baixados a cada execução como se fossem vagas novas. Novos links permanecem candidatos até revisão.

## Correções em preparação para aprovação (11/11/2026)

O pacote de auditoria ainda não foi aplicado ao site. A proposta consulta todas as URLs explicitamente cadastradas, registra falhas de navegação e distingue instituições tentadas de páginas com leitura. O reconhecimento de candidatos considera títulos e caminhos de editais, inclusive âncoras genéricas e cargos em inglês/espanhol. O portal Gupy da PUCRS foi acrescentado a partir do link institucional observado.

A interface exige prazo ISO válido e revisão de até sete dias; favoritas usam seu próprio filtro. O campo legado Validada passa a respeitar atualização e falhas documentais. Isso não altera requisitos de elegibilidade. Mudanças de decodificação podem alterar hashes de documentos e exigir nova revisão, sem promoção automática.

Para simular sem modificar o catálogo de trabalho, copie os quatro arquivos de entrada (vagas.json, instituicoes.json, revisoes.json, oportunidades_curadas.json) para uma pasta e execute `RADAR_DATA_DIR=/caminho/da/copia python scripts/atualizar_vagas.py`. O programa impede gravação se faltar registro histórico ou se todas as instituições falharem. Backups do navegador continuam sendo responsabilidade do usuário; o coletor não acessa dados locais de candidaturas.

A proposta usa Ubuntu 24.04, checkout v5, setup-python v6 e setup-node v5 com Node 24 explícito. A rotina diária às 11:00 UTC permanece. Testes após coleta precedem a gravação no GitHub. A validação hospedada desta nova configuração só poderá ser concluída após autorização de publicação; os testes locais não equivalem a execução no runner Ubuntu.
