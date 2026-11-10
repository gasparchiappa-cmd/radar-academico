# Radar Acadêmico

Monitoramento diário de oportunidades acadêmicas, com prioridade a graduados em Fisioterapia com doutorado.

## Funcionamento

- `instituicoes.json`: fontes institucionais configuráveis, com 16 instituições do RS e expansão inicial nacional e internacional.
- `scripts/atualizar_vagas.py`: consulta direta, navegação limitada a três páginas de recrutamento por instituição, leitura dos candidatos, deduplicação de URLs e auditoria da execução.
- `scripts/noticias.py`: consultas complementares ao Google Notícias, incluindo trabalho remoto.
- `vagas.json`: histórico preservado. Candidatos não são vagas confirmadas.
- `monitoramento.json`: última tentativa de consulta, falhas, consultas parciais e contagens.
- `index.html`: catálogo sincronizado e controle local de candidaturas. A chave `radar-fisio-v1` foi preservada.

## Evidência e validação

A extração de indícios não confirma elegibilidade. Cada registro contém campos para graduação, doutorado, idioma, nacionalidade, residência, autorização profissional e trabalho a partir do Brasil. Prazos, remuneração e requisitos desconhecidos permanecem não informados. Cadastro reserva não garante contratação.

Uma oportunidade somente recebe `Validada` quando `validacao_documental` contém revisor, data, URL oficial, decisões explícitas de elegibilidade para Fisioterapia/doutorado e de remuneração, e `valor` e `evidencia` para todos os requisitos, prazo e remuneração. Evidências devem ser trechos do edital ou anexos, inclusive quando documentarem isenção ou ausência de exigência. O prazo ISO deve ser confirmado em `prazo`. Não preencha com inferências. Validação exige revisão de anexos e retificações. Prazo anterior à data de Brasília resulta em `Encerrada`; prazo ausente nunca significa aberta.

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
