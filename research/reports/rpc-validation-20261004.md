# Validação RPC — 2026-10-04

Status: campanha interrompida antes da matriz completa. Resultados incompletos não são válidos para comparação.

## Protocolo congelado

Qwen2.5-1.5B-Instruct Q5_K_M, SHA-256 `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`; prompt `Write exactly one short sentence about distributed computing.`; 38 tokens de entrada; contexto 512; saída máxima 32; temperatura 0; seed 42; 4 threads; `-ngl 99`; `--ignore-eos`; sem warmup; processo frio por caso; timeout uniforme de 240 s com 10 s de encerramento.

Runtime fixado no commit `68e79bd8cd6b7995f8fce8da252b249bbf237e63`, com patch local de compilação `-O0` preservado em `common/CMakeLists.txt` e `vendor/cpp-httplib/CMakeLists.txt`. Cliente SHA-256 `13b3c2e9b45a75615bf9ea11d1c98e182cfcd37e505c7aae9df2e332b5348d69`; pacote ARM SHA-256 `7f312b05110ae904a56943e71042165b3d72f32000b9820d07831746e5441148`.

## Evidência válida

O piloto `20261004T-pilot2-instrumented-6` comprovou uso efetivo de dois workers: camadas 0–14 em `192.168.50.42` e 15–28 em `192.168.50.118`; ambos registraram `graph_compute` (3), `graph_recompute` (30), `get_tensor` (33) e transferências durante a mesma requisição. Foram gerados 32 tokens: prompt 31.028 s/38 tokens, geração 36.920 s/32 tokens, total interno 67.948 s; tempo de processo 168.34 s. O notebook executou coordenação, backend CPU e parte não remota do grafo.

## Campanhas preservadas

- `20261004T-matrix-validation-1`: 5 notebooks válidos; 5 ARM falharam pelo uso inexistente de `/usr/bin/time`; nenhum RPC foi coletado nessa tentativa.
- `20261004T-matrix-validation-2`: 2 ARM válidos; processo interrompido antes do restante.
- `20261004T-matrix-validation-5`: 5 ARM válidos; dois workers falharam por indisponibilidade de `192.168.50.118`; não houve inferência válida.
- `20261004T-matrix-validation-6`: 2 de 5 casos de dois workers válidos em terminal interativo; os demais foram interrompidos pelo controle de entrada do terminal.
- `20261004T-matrix-validation-7`: caso incompleto: ambos receberam tensores e camadas, mas o timeout ocorreu no carregamento (`command_exit=137`) antes de tokens.

As campanhas `-3` e `-4` registram falhas de ambiente/sandbox antes de inferência. O caso de oito workers não foi iniciado.

## Conclusão e lacunas

**Observação:** há prova instrumental de distribuição efetiva em dois workers em um piloto controlado. **Hipótese:** a variabilidade atual parece relacionada à disponibilidade/estado dos servidores e ao modo de entrada do cliente; não permite atribuir um limite ao RPC. **Conclusão:** ainda não há cinco repetições válidas para notebook, Labrador e dois workers, nem base para comparar quatro, seis ou oito workers.

Próxima campanha: executar cliente sem TTY e com EOF explícito, validar saúde dos dois workers antes de cada caso, completar cinco repetições das três linhas de base e só então avançar para quatro, seis e piloto de oito. Não usar distributed-llama, modelo maior ou 16 nós nesta etapa.
