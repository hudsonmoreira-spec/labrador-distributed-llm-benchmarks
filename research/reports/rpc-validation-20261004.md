# Validação RPC — 2026-10-04

Status: conjunto A/B/C fechado para o recorte do artigo. A matriz ampla histórica não foi continuada; resultados incompletos permanecem preservados e fora dos agregados.

## Protocolo congelado

Qwen2.5-1.5B-Instruct Q5_K_M, SHA-256 `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`; prompt `Write exactly one short sentence about distributed computing.`; 38 tokens de entrada; contexto 512; saída máxima 32; temperatura 0; seed 42; 4 threads; `-ngl 99`; `--ignore-eos`; sem warmup; processo frio por caso; timeout uniforme de 240 s com 10 s de encerramento.

Runtime fixado no commit `68e79bd8cd6b7995f8fce8da252b249bbf237e63`, com patch local de compilação `-O0` preservado em `common/CMakeLists.txt` e `vendor/cpp-httplib/CMakeLists.txt`. Cliente SHA-256 `13b3c2e9b45a75615bf9ea11d1c98e182cfcd37e505c7aae9df2e332b5348d69`; pacote ARM SHA-256 `7f312b05110ae904a56943e71042165b3d72f32000b9820d07831746e5441148`.

## Evidência válida

O piloto `20261004T-pilot2-instrumented-6` comprovou uso efetivo de dois workers: camadas 0–14 em `192.168.50.42` e 15–28 em `192.168.50.118`; ambos registraram `graph_compute` (3), `graph_recompute` (30), `get_tensor` (33) e transferências durante a mesma requisição. Foram gerados 32 tokens: prompt 31.028 s/38 tokens, geração 36.920 s/32 tokens, total interno 67.948 s; tempo de processo 168.34 s. O notebook executou coordenação, backend CPU e parte não remota do grafo.

## Campanhas preservadas

- `20261004T-matrix-validation-1`: 5 notebooks válidos; 5 ARM falharam pelo uso inexistente de `/usr/bin/time`; nenhum RPC foi coletado nessa tentativa.
- `20261004T-matrix-validation-2`: 5 ARM válidos com `command_exit=0`; os ensaios RPC subsequentes falharam na conexão e não são comparáveis.
- `20261004T-matrix-validation-5`: 5 ARM válidos; dois workers falharam por indisponibilidade de `192.168.50.118`; não houve inferência válida.
- `20261004T-matrix-validation-6`: 2 de 5 casos de dois workers válidos em terminal interativo; os demais foram interrompidos pelo controle de entrada do terminal.
- `20261004T-matrix-validation-7`: `rep-1` terminou por timeout durante carregamento (`command_exit=137`), `rep-2` foi interrompida (`124`), `rep-3` e `rep-4` concluíram normalmente (`command_exit=0`) com 32 tokens e operações registradas nos dois workers; `rep-5` abortou após transmitir 30 tokens (`command_exit=134`) e é inválida para métricas finais.

As campanhas `-3` e `-4` registram falhas de ambiente/sandbox antes de inferência. A campanha `20261004T-rpc2-complete-1` completou as três repetições que faltavam, todas com health-check aprovado, `command_exit=0`, 32 tokens e operações nos dois workers. O CSV reconstruído está em [`research/data/derived/rpc-validation-20261004.csv`](../data/derived/rpc-validation-20261004.csv), e o resumo estatístico em `rpc-validation-20261004-summary.csv`. O caso de oito workers não foi iniciado.

A campanha histórica `20261004T-replicates-rpc-3` concluiu 20/20 processos, mas sua instrumentação não comprovou execução efetiva em cada worker; ela permanece como contexto histórico e não é misturada ao conjunto do artigo. As classes de falha auditadas são: preparação (`/usr/bin/time` ausente no ARM em `matrix-validation-1`), conexão (worker RPC indisponível em `matrix-validation-5`), carregamento/timeout (`matrix-validation-7/rep-1`), execução interativa ou interrompida externamente (`rep-2` e `matrix-validation-6`) e encerramento anormal após geração parcial (`matrix-validation-7/rep-5`). O código de saída zero só foi aceito quando também havia métricas de fase, contagem de tokens e evidência dos dois servidores.

## Conclusão e lacunas

**Observação:** há prova instrumental no piloto e cinco execuções RPC válidas, todas com camadas e operações nos dois workers. As médias das execuções válidas são: notebook 5,69 s de processo; ARM 43,86 s; RPC-2 168,67 s, com 31,08 s de prompt, 36,91 s de geração e 32 tokens gerados. **Hipótese:** o custo RPC observado é dominado por comunicação e execução distribuída; essa hipótese não deve ser tratada como causalidade sem novas medições. **Conclusão:** a comparação essencial A/B/C agora tem cinco execuções válidas por condição sob o protocolo controlado. Não há base nem necessidade, no escopo atual do artigo, para comparar quatro, seis ou oito workers.

O conjunto selecionado para análise tem cinco tentativas por condição e taxa de sucesso condicionada de 5/5 em cada condição. Isso não é a taxa operacional de todas as tentativas: o inventário completo inclui falhas de preparação, conexão, carregamento, interação e encerramento. Não iniciar novos testes RPC nem ampliar para quatro, seis, oito ou 16 nós nesta etapa; a próxima ação é a revisão dos autores do manuscrito em `paper/icce2027/`.
