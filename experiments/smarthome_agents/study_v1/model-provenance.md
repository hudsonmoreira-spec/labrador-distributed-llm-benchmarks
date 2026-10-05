# Modelos e runtime

Bases oficiais verificadas em 2026-10-05:

- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct — Qwen, 0.49B parâmetros segundo model card, Apache-2.0.
- https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct — Qwen, Apache-2.0.
- https://github.com/ggml-org/llama.cpp/blob/e25a32e98/tools/server/README.md — documentação do endpoint de chat/saída estruturada correspondente à revisão do runtime.

Arquivos GGUF preexistentes: nomes internos qwen2.5-0.5b-instruct / qwen2.5-1.5b-instruct, arquitetura qwen2, 24/28 blocos e `general.file_type=17` (Q5_K_M). Metadados extraídos por `read_gguf_metadata.py`, preservando somente metadados e comprimentos das grandes listas de vocabulário. Os campos `general.size_label` dos arquivos são 630M/1.8B: não substituem os nomes de família nem as contagens oficiais de parâmetros das bases. Não foi preservada uma cadeia verificável da conversão original; o manuscrito deve explicitar essa limitação e a avaliação dos arquivos locais identificados por hash, sem atribuir sua conversão ao fornecedor oficial.

0.5B SHA-256: `041474553fcabfc2a2d67903f9d2c2e50bd92528e670da4f33b5d0ce6e59fd55`.

1.5B SHA-256: `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`.

Runtime `llama-server`: SHA-256 `a46782e75231c0a4a75a1e38afbbc5d7b72d92c8d834d6bb8b5020a0e1e79a87`, versão 9584/e25a32e98, GCC 12.2.0 ARM64. Conferir bibliotecas e modelos em todos os hosts antes do congelamento. O mesmo nome de binário não basta para padronização.
