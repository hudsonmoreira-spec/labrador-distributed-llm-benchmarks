# Modelos e runtime

Bases oficiais verificadas em 2026-10-05:

- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct — Qwen, 0.49B parâmetros segundo model card, Apache-2.0.
- https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct — Qwen, Apache-2.0.
- https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md — documentação oficial atual do endpoint de chat e saída estruturada, consultada em 2026-10-05. A tentativa de recuperar a página da revisão curta e25a32e98 pela ferramenta web falhou; a configuração efetiva é conferida nas propriedades e respostas do runtime local. Não afirmar que a página consultada é um snapshot dessa revisão.

Arquivos GGUF preexistentes: nomes internos qwen2.5-0.5b-instruct / qwen2.5-1.5b-instruct, arquitetura qwen2, 24/28 blocos e `general.file_type=17` (Q5_K_M). Metadados extraídos por `read_gguf_metadata.py`, preservando somente metadados e comprimentos das grandes listas de vocabulário. Os campos `general.size_label` dos arquivos são 630M/1.8B: não substituem os nomes de família nem as contagens oficiais de parâmetros das bases. Não foi preservada uma cadeia verificável da conversão original; o manuscrito deve explicitar essa limitação e a avaliação dos arquivos locais identificados por hash, sem atribuir sua conversão ao fornecedor oficial.

0.5B SHA-256: `041474553fcabfc2a2d67903f9d2c2e50bd92528e670da4f33b5d0ce6e59fd55`.

1.5B SHA-256: `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`.

Runtime `llama-server`: SHA-256 `a46782e75231c0a4a75a1e38afbbc5d7b72d92c8d834d6bb8b5020a0e1e79a87`, versão 9584/e25a32e98, GCC 12.2.0 ARM64. Conferir bibliotecas e modelos em todos os hosts antes do congelamento. O mesmo nome de binário não basta para padronização.

## Referências e notas de leitura

Metadados e primeira página dos artigos conferidos nas fontes primárias em 2026-10-05, sem copiar PDFs ao Git:

- HomeBench: https://aclanthology.org/2025.acl-long.597/ e PDF oficial. Autores e publicação coincidem com o BibTeX da prévia. A seção 1 e a figura 1 distinguem instruções e propostas válidas/indevidas em dispositivos existentes ou inexistentes; a seção de construção descreve um ambiente virtual maior. Nosso estudo conserva a distinção de erro, mas usa dois cômodos, iluminação e linguagem portuguesa, sem reutilizar ou representar a cobertura do benchmark.
- Demystifying Small Language Models for Edge Deployment: https://aclanthology.org/2025.acl-long.718/ e PDF oficial. Autores/publicação coincidem com o BibTeX. Leitura orientada à relação entre capacidade do modelo e custo de implantação. O artigo motiva medir qualidade e eficiência conjuntamente; não serve como evidência de vantagem de um tamanho de Qwen em Labrador.

BibTeX verificado está preservado em `paper/smarthome_agents/preview_20261005/references.bib`; a versão final deverá copiá-lo para sua própria pasta. A nota inicial da prévia permanece imutável; esta nota registra a verificação posterior do PDF oficial.
