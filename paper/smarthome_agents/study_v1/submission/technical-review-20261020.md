# Revisão técnica e bibliográfica — smart home — 2026-10-20

## Escopo e resultado

A preparação foi aplicada ao artigo de **casa inteligente simulada**, em `paper/smarthome_agents/study_v1/`. O artigo RPC, seus experimentos e seus arquivos permanecem preservados e não foram usados como resultados desta revisão.

Foram revisados os manuscritos inglês e português, a argumentação, referências, identificação das evidências, autoria, contato, financiamento e declaração de uso de IA. O resumo do EDAS foi preparado a partir do LaTeX inglês. Não foi realizado cadastro ou envio ao ICCE/EDAS; o usuário determinou que a submissão permaneça em espera.

## Alterações editoriais e científicas

- Atualizados os seis autores na ordem já confirmada, todos USP; Hudson Moreira Guimarães dos Santos é o correspondente (`hudson.moreira@usp.br`). E-mail de Pablo permanece pendente somente nos dados de cadastro; não foi inventado.
- Retiradas as marcas “Version for advisor review” e de autoria proposta. Registrada ausência de financiamento externo conforme informado pelo usuário.
- Título passou de “Accuracy … Scalability” para “Task Success … Replication”, para refletir sucesso nas tarefas construídas e replicação de servidores, sem sugerir precisão residencial populacional ou capacidade máxima.
- Pergunta de pesquisa e contribuições explicitam avaliação de decisões, intervenção do executor e atendimento em lotes fechados.
- Removido do corpo de resultados o piloto com executor antigo; suas evidências históricas permanecem intactas no repositório e não são somadas ao estudo reservado.
- Texto de resultados condensado e conferido contra tabelas/JSONs; mantida a distinção entre resposta fora do contrato e comandos individuais indevidos.
- RAM visível corrigida para cerca de 1,89 GiB a partir dos registros das seis placas; não importada do experimento RPC.
- Incluídos endereço imutável das evidências, documentação do runtime na revisão exata e orientação IEEE de uso de IA.
- Acrescentada análise de sensibilidade dos quatro julgamentos assistidos, sem alterar o ledger nem atribuir revisão humana.

## Evidências e reconstrução

[Relatório da auditoria pública](../artifact/public-evidence-audit-20261020.json), [manifesto](../artifact/evidence-manifest.json) e [guia de reprodução](../artifact/README.md).

O snapshot `a834b8255f736fb59425b146be183c17866a2c7d` foi baixado anonimamente do GitHub. Passaram 3.021 hashes, os 18 arquivos congelados, 27 arquivos de análise e 19 fontes/resumos gerados com igualdade byte a byte. Os verificadores existentes reexecutam o avaliador sobre cada resposta e conferem estado, permissões e julgamento registrados.

Também foram conferidos: 240 tentativas de qualidade, 108 de replicação, 18 janelas de lotes calculadas dos timestamps, ausência de inferências sobrepostas por placa, parâmetros de requisição e sequência temporal após o congelamento; identidade registrada dos modelos, runtime/bibliotecas e configuração nas seis placas. As duas campanhas de desenvolvimento têm 48 tentativas cada e ficam separadas.

O gerador de figuras/tabelas recebeu apenas opções explícitas de data/commits, permitindo reconstrução determinística de arquivos extraídos sem `.git`. Avaliador, executor, cenários e scripts congelados não foram modificados. As fontes científicas geradas continuam idênticas às do snapshot.

## Resultados conferidos

| Condição | Sucessos automáticos | Mediana HTTP (s) | p95 (s) | Comandos indevidos / bloqueados |
|---|---:|---:|---:|---:|
| Regras | 42/80 | 0,157 | 0,643 | 0 / 0 |
| Qwen 0.5B | 30/80 | 36,848 | 45,292 | 36 / 16 |
| Qwen 1.5B | 12/80 | 94,663 | 159,117 | 76 / 22 |

Todos os 240 retornos foram estruturados válidos. RSS mediano pós-requisição: 571,6 MiB e 1183,7 MiB para 0.5B e 1.5B; não é pico individual nem RAM física exclusiva. As taxas dos modelos em 1/3/6 réplicas coincidem com as tabelas e figuras. A taxa excepcionalmente alta das regras com seis réplicas decorre da janela de aproximadamente 9–11 ms e da ausência de intervalos entre ondas, não de capacidade sustentada medida.

### Julgamentos assistidos

Os quatro registros do 0.5B foram mantidos como `human_validation_pending=true`. São duas ocorrências de “Quero a luz acender.” e duas de “Pode apagar a iluminação?”. Nenhum sucesso depende da classificação assistida. Mesmo aceitando todas como corretas, o resultado seria 34/80 (42,5%), abaixo das regras (52,5%). O manuscrito comunica o caráter provisório; a concordância geral dos autores não foi usada como validação específica dos quatro casos.

## Conferência das referências

[Metadados dos artigos](../artifact/bibliographic-verification-20261020.json) e [modelos/runtime](../artifact/model-reference-verification-20261020.json).

- **HomeBench:** autores, título, ACL 2025, pp. 12230–12250 e DOI conferidos na [ACL Anthology](https://aclanthology.org/2025.acl-long.597/). PDF oficial consultado na definição de ambiente virtual e instruções válidas/inválidas. Não é usado como comparação numérica nem como origem do conjunto de 40 casos.
- **Demystifying Small Language Models for Edge Deployment:** autores, ACL 2025, pp. 14747–14764 e DOI conferidos na [ACL Anthology](https://aclanthology.org/2025.acl-long.718/). PDF oficial consultado nas análises de capacidade, prefill/decode, quantização e hardware; não sustenta conclusões sobre desempenho em Labrador.
- **Qwen 0.5B e 1.5B:** model cards oficiais conferidos. Metadados oficiais dos GGUF confirmam os SHA-256 `041474…59fd55` e `b46661…896f8c`, coincidentes com os seis hosts. As revisões dos repositórios Hugging Face e tamanhos estão registrados no relatório, sem baixar pesos.
- **llama-server:** documentação conferida na revisão completa `e25a32e98c15a1118a976685af0f4d2c1f380079`, com suporte a esquema JSON, slots e cache de prompt. A referência deixou de apontar para `master`.
- **Artefato:** citado o snapshot de smart home, não o commit do artigo RPC. Dados, falhas e scripts acessíveis sem autenticação e reconstruídos.
- **Uso de IA:** declaração identifica Codex e as atividades realizadas, distinguindo julgamentos assistidos de humanos, conforme a [orientação IEEE](https://open.ieee.org/author-guidelines-for-artificial-intelligence-ai-generated-text/).

Não foram acrescentadas referências apenas para aumentar a bibliografia. A relação com os dois estudos de pesquisa é específica e os demais itens identificam modelos, runtime, evidência e política editorial.

## Limites científicos mantidos

Conjunto pequeno, elaborado pelos autores, em português e com duas luzes; casos não representam casas independentes. Ausência de pedidos idempotentes e estados inicialmente opostos favorecem estratégias simples de inversão. Regras finitas não são um baseline linguístico ótimo. Um prompt, esquema e quantização por tamanho não isolam efeito de parâmetros. Duas repetições por cenário não são amostras independentes para precisão populacional. Processos residentes e serviços anteriores impedem afirmar uso exclusivo da placa. Escala em poucos lotes instrumentados não é saturação. Não há energia, pico por requisição, atuação física, segurança residencial ou usabilidade real medidos.

Esses limites são declarados e não foram corrigidos por suposições ou novas coletas. A revisão preserva todos os resultados reservados e o congelamento.

## PDF, preparação e pendências

Ambos os PDFs foram recompilados do LaTeX e renderizados para inspeção de todas as páginas. A conferência objetiva e os hashes estão em [pdf-check-20261020.json](pdf-check-20261020.json). O inglês é o candidato para ICCE; o português é material de leitura.

Campos técnicos e dados dos autores: [edas-draft.md](edas-draft.md). Falta o e-mail de Pablo para completar os contatos. Eventuais campos e declarações adicionais devem ser tratados conforme o formulário real do EDAS. Não se exige novo documento de aprovação de coautores. **Nada deve ser cadastrado ou submetido ao ICCE/EDAS sem nova instrução do usuário.**
