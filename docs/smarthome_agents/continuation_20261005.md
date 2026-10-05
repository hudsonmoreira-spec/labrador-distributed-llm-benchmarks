# Continuidade da campanha reduzida

## Entregas preservadas

- `cd85d1c`: prévia portuguesa IEEE em `paper/smarthome_agents/preview_20261005/main.pdf`, revisada em duas páginas, fonte, script de reconstrução e decisões editoriais. Commit publicado em `origin/smarthome-multiagent`.
- `e457881`: executor sem consulta ao gabarito, revisão conservadora de esclarecimento e testes. Ainda publicar junto à entrega de desenvolvimento.
- Primeiro artigo e evidências anteriores permanecem em seus caminhos originais. Alterações locais de inventário e logs de outros estudos não foram incluídas nesses commits.

## Estado da nova campanha

O protocolo reduzido candidato está em `experiments/smarthome_agents/study_v1/protocol.md`; 8 casos de desenvolvimento e 40 reservados. Os reservados ainda não foram executados. `freeze.json` só deverá ser gerado após desenvolvimento concluído e conferência dos hashes dos seis hosts. Sem ajustes com base no reservado.

Scripts novos: `prepare_hosts_v1.py`, `deploy_rules_v1.py`, `study_v1.py`, `run_study_v1.py`, `analyze_study_v1.py`, `read_gguf_metadata.py`. Testes locais: 20 passaram.

Preparação inicial preservada: biblioteca faltava no LD_LIBRARY_PATH de comandos de verificação. Segunda preparação e recuperação preservam logs separados. O reinício do servidor Codex interrompeu a preparação local, sem campanha reservada iniciada. Cinco hosts saudáveis em 19000/19005/19015; .85 estava pendente de transferência/inicialização na recuperação. Confirmar estado real dos serviços antes de repetir operações.

Próximos passos: concluir .85, conferir propriedades/runtime/hash e fontes da referência por regras; registrar commit de desenvolvimento; executar `--phase development` em nova pasta; analisar sem reservado; congelar scripts e protocolo por hash em commit; qualidade 240 tentativas e escala 108; análise e manuscritos atualizados inglês/português; revisão visual e commits/publicação.

A sexta placa foi substituída de .85/lab4 para .200/lab6 antes do desenvolvimento, por conexões interrompidas/atrasadas na preparação. Mesmo runtime conferido. Sem aumentar número de placas ou mudar categorias. Não usar .85 nas campanhas.
