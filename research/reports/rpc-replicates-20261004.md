# Campanha RPC replicada — 2026-10-04

## Estado da execução

A campanha terminou normalmente com **20/20 casos concluídos**, todos com `command_exit=0` e saída textual. Não houve timeout nesta execução. O conjunto foi:

- baseline do notebook: 5 repetições;
- notebook coordenando 2 workers RPC: 5 repetições;
- notebook coordenando 4 workers RPC: 5 repetições;
- notebook coordenando 6 workers RPC: 5 repetições.

Não houve nova execução com 8 workers nesta campanha. O ensaio anterior de 8 workers com 90 s não é comparável aos casos desta campanha, que usaram `timeout 240s` com encerramento forçado 10 s depois. Portanto, não há base uniforme para declarar um limite em 8 workers.

## Configuração preservada

- Run: `20261004T-replicates-rpc-3`.
- Modelo: Qwen2.5-1.5B-Instruct Q5_K_M, SHA-256 `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`.
- Cliente: `llama-cli`, commit `68e79bd8cd6b7995f8fce8da252b249bbf237e63`, SHA-256 `13b3c2e9b45a75615bf9ea11d1c98e182cfcd37e505c7aae9df2e332b5348d69`.
- Parâmetros: contexto 512, quatro threads, `-ngl 99`, prompt `Generate a short sentence about distributed computing.`, `-n 64`.
- Timeout: 240 s, seguido de 10 s para encerramento forçado.
- Workers: `192.168.50.42`, `.118`, `.231`, `.74`, `.44` e `.75`, porta 50052.
- Build local do cliente: `GGML_RPC=ON`, `LLAMA_BUILD_SERVER=ON`, `-DGGML_SCHED_MAX_BACKENDS=32`; o cache local também registra `GGML_NATIVE=ON`, apropriado ao notebook x86-64.
- Patch local preservado: hash SHA-256 `58e8ea08a8052f4732fda28537ae90e870e587102a3a9b6e1f49b33f26ecde44` sobre as alterações em `common/CMakeLists.txt` e `vendor/cpp-httplib/CMakeLists.txt`. O patch aplica `-O0` a esses alvos para contornar falhas de compilação; não altera o commit-fonte do llama.cpp.
- Artefato ARM usado nos workers: `llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp`, pacote SHA-256 `7f312b05110ae904a56943e71042165b3d72f32000b9820d07831746e5441148`; build com `GGML_NATIVE=OFF`, `GGML_RPC=ON`, RDMA/CUDA/Vulkan/Metal/OpenMP desabilitados, GCC 12 e sysroot Debian 12.
- Cache do cliente local: `CMakeCache.txt` SHA-256 `dba560a6bfec3575d9d8be4c3e2bcf5ba8009e485634f0ddf2f084639653b729`; `compile_commands.json` SHA-256 `78b3f8b821ebff25dee578816ce70095060dcbf3db7ba7bc13dc3027190b92b1`.

Patch textual preservado para auditoria:

```diff
+target_compile_options(${TARGET} PRIVATE -O0)
+set_source_files_properties(httplib.cpp PROPERTIES COMPILE_OPTIONS "-O0")
```

O primeiro trecho está em `common/CMakeLists.txt`; o segundo, em `vendor/cpp-httplib/CMakeLists.txt`.

## Tempos observados

Os tempos abaixo são tempo real do processo completo, incluindo carregamento, sincronização, processamento do prompt e geração. A instrumentação atual não separa esses componentes em segundos.

| Configuração | n | Média (s) | Desvio-padrão (s) | Mín–máx (s) | Sucesso |
|---|---:|---:|---:|---:|---:|
| Notebook sozinho (`rpc_hosts=0`) | 5 | 4,97 | 0,16 | 4,81–5,21 | 5/5 |
| Notebook + 2 RPC | 5 | 163,23 | 4,99 | 155,68–169,71 | 5/5 |
| Notebook + 4 RPC | 5 | 162,38 | 2,34 | 159,20–166,40 | 5/5 |
| Notebook + 6 RPC | 5 | 160,27 | 3,37 | 155,87–164,60 | 5/5 |

O cliente exibiu, no baseline, prompt de 27,9–30,4 t/s e geração de 12,5–13,1 t/s. Nos casos RPC, exibiu prompt de 1,2 t/s e geração de 0,8 t/s. Esses valores são métricas agregadas do cliente, não uma decomposição de carregamento/prompt/geração por worker.

## Linhas de base e interpretação

- **Notebook sozinho:** presente como `rpc_hosts=0`; o modelo é executado localmente.
- **Labrador sozinho:** ausente nesta campanha. Não foi executado um baseline usando um único host ARM como cliente/modelo completo.
- **Notebook coordenando N workers:** presente para N=2, 4 e 6. O notebook continua executando a parte local do scheduler/backend CPU; a linha de comando não prova qual camada foi atribuída a cada backend.

Os resultados demonstram que o cliente completa a inferência com as listas RPC de 2, 4 e 6 hosts. Eles não demonstram, sozinhos, que todos os workers receberam camadas ou tensores da mesma inferência.

## Verificação dos workers

Os snapshots antes/depois registraram a porta 50052 como `listening` nos seis hosts. Os logs agregados dos servidores registraram conexões aceitas e encerradas, mas não registraram eventos identificáveis de `init_tensor`, `set_tensor`, execução de operador, distribuição de camadas ou IDs de requisição. Assim:

- servidor conectado: **confirmado**;
- servidor efetivamente utilizado na mesma inferência: **não comprovado pela instrumentação desta campanha**;
- distribuição de camadas/tensores: **não registrada**.

Esta é uma lacuna de validade, não um resultado negativo. A próxima campanha precisa habilitar logging/telemetria por requisição ou coletar contadores de operações no RPC, preservando o mesmo modelo e protocolo.

## Tokens e decomposição temporal

`-n 64` define um máximo, não uma quantidade garantida. Os logs preservam o texto produzido e as taxas agregadas, mas não registram o número real de tokens emitidos; portanto, não é válido calcular tokens/s efetivos a partir desta campanha. Também não há tempos separados de carregamento, prompt e geração. Esses dois campos devem ser adicionados antes de qualquer tabela de eficiência.

## Evidências e lacunas

Os artefatos brutos estão em [rpc-replicates](../data/runs/20261004T-replicates-rpc-3/rpc-replicates), incluindo `manifest.txt`, logs, tempos, status, snapshots e `progress.log`. O script é [rpc_replicates.sh](../scripts/rpc_replicates.sh).

O percentual geral do projeto permanece em **40%** no relatório de progresso: a campanha RPC foi concluída, mas os critérios documentados para validar a matriz completa exigem participação efetiva dos workers, decomposição temporal e contagem real de tokens. Não foi aplicada uma nova porcentagem.

## Próxima campanha proposta

Antes de repetir configurações, instrumentar o cliente/servidor para registrar: conexão por caso, operações RPC por worker, tensores/camadas atribuídos, tokens emitidos, tempo de carregamento, prompt e geração. Em seguida, repetir somente as medições necessárias, incluindo o baseline Labrador isolado e um teste de 8 workers com o mesmo timeout uniforme de 240 s + 10 s. O modelo, prompt, contexto, binários e opções devem permanecer fixos.
