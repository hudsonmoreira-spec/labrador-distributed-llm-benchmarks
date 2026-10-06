# Registro de pausa e retomada — 2026-10-06

Atividade pausada a pedido do usuário. Nesta preparação foram feitas apenas consultas de Git, arquivos locais e processos/portas por SSH. Nenhum novo experimento, inferência, alteração de resultado ou intervenção nos serviços foi executado.

## Git e alterações pendentes

Branch: `smarthome-multiagent`. Último commit publicado **antes deste registro**: `de63a087cdc849979787ab41dd576a8a8ae02f57`, igual a `origin/smarthome-multiagent` na conferência inicial. O commit deste documento será o novo ponto de retomada, identificável por `git log -1 -- docs/smarthome_agents/continuation_20261006.md`. Publicar somente na mesma branch, sem merge em main.

Alterações locais anteriores preservadas e excluídas do commit de pausa (`M`: modificado; `??`: não rastreado):

```text
 M research/data/inventory.csv
 M research/data/inventory.json
 M research/reports/inventory_report.md
?? CHECKPOINT_codex_2026-10-03.md
?? models/
?? ops/convacare-access-report.sh
?? research/data/runs/20261001T180524Z/controller/
?? research/data/runs/20261001T180524Z/diagnostics/
?? research/data/runs/20261001T180524Z/hosts/
?? research/data/runs/20261003T-replicates-rpc-2-launcher.log
?? research/data/runs/20261004T-pilot2-instrumented-1/
?? research/data/runs/20261004T-pilot2-instrumented-2/
?? research/data/runs/20261004T-pilot2-instrumented-3/
?? research/data/runs/20261004T-pilot2-instrumented-4/
?? research/data/runs/20261004T-pilot2-instrumented-5/
?? research/data/runs/20261004T-replicates-rpc-3-launcher.log
?? research/data/runs/20261005T122157Z/
```

Nenhuma alteração experimental ou de manuscrito estava pendente. Este documento é a única alteração do commit de pausa. Não adicionar inventários, modelos, CHECKPOINT ou logs de outros trabalhos.

## Campanhas concluídas

- **Qualidade: 240/240 tentativas**, 40 cenários × duas repetições × três condições; commit `938184b`. Regras 42/80, 0.5B 30/80, 1.5B 12/80.
- **Escala: 108/108 tentativas**, 18 lotes de seis pedidos, em uma/três/seis placas; commit `d2efabd`, incluindo auditoria final.
- Ambos os diretórios têm `completed.json`; contagens dos arquivos individuais reconferidas nesta pausa.
- Desenvolvimento: duas campanhas completas de 48 tentativas, preservadas.
- Manifesto `experiments/smarthome_agents/study_v1/freeze.json`, commit `2bab455`, código de referência `72beda0`: os 18 hashes congelados foram reconferidos sem divergência.
- Taxas de escala usam janela HTTP instrumentada, não tempo até mudança de estado ou capacidade máxima. Repetições agrupadas por cenário. Toda ação exclusivamente simulada.

## PDFs, fontes, dados e reprodução

Caminhos relativos à raiz do repositório:

| Artefato | Caminho |
|---|---|
| PDF PT, quatro páginas revisadas | `paper/smarthome_agents/study_v1/main_pt.pdf` |
| PDF EN, quatro páginas revisadas | `paper/smarthome_agents/study_v1/main_en.pdf` |
| Fontes LaTeX | `paper/smarthome_agents/study_v1/main_pt.tex` e `paper/smarthome_agents/study_v1/main_en.tex` |
| Bibliografia e notas | `paper/smarthome_agents/study_v1/references.bib` e `paper/smarthome_agents/study_v1/reading-notes.md` |
| Prévia inicial preservada | `paper/smarthome_agents/preview_20261005/main.pdf` e `main.tex` na mesma pasta |
| Primeiro artigo preservado | `paper/icce2027/` |
| Dados brutos de qualidade | `experiments/smarthome_agents/runs/20261006-study-v1-quality/` |
| Dados brutos de escala | `experiments/smarthome_agents/runs/20261006-study-v1-scale/` |
| Análises | `experiments/smarthome_agents/analysis/quality-v1/` e `experiments/smarthome_agents/analysis/scale-v1/` |
| Auditoria final | `experiments/smarthome_agents/runs/20261006-study-v1-final-audit/` |
| Cenários/configurações/manifesto | `experiments/smarthome_agents/study_v1/` |
| Comandos completos de reprodução | `paper/smarthome_agents/study_v1/README.md` |
| Análise congelada | `experiments/smarthome_agents/scripts/analyze_study_v1.py` |
| Análise por comando | `experiments/smarthome_agents/scripts/analyze_action_steps_v1.py` |
| Tabelas e figuras reproduzíveis | `experiments/smarthome_agents/scripts/make_study_assets.py` |
| Executor da campanha, não iniciar nesta pausa | `experiments/smarthome_agents/scripts/run_study_v1.py` |
| Relatórios | `docs/smarthome_agents/quality_20261006.md` e `docs/smarthome_agents/scale_20261006.md` |

Logs, requisições, respostas, falhas e evidências anteriores permanecem preservados. Não alterar fontes congeladas nem sobrescrever campanhas.

## Pendências

Revisão dos orientadores dos PDFs PT/EN, resultados, limitações e requisitos editoriais. Autoria e ordem **propostas**: Hudson Moreira; Marcelo Knörich Zuffo; Laisa Costa de Biase. Confirmar afiliações, departamentos, e-mails e identificadores, sem inventar metadados.

Quatro julgamentos semânticos assistidos por Codex, **não revisão humana**, aguardam apreciação: duas frases “Quero a luz acender.” e duas perguntas “Pode apagar a iluminação?”. Foram julgadas falhas por não solicitar o cômodo ausente, sem conceder sucesso. Ledger: `experiments/smarthome_agents/runs/20261006-study-v1-quality/manual_reviews.json`. Nenhum sucesso depende desses julgamentos; originais intactos.

Demais decisões editoriais e uso de IA: `paper/smarthome_agents/study_v1/review.md`. Nenhuma mensagem foi enviada aos orientadores.

## Serviços ainda ativos nas Labradores

Consulta por SSH em **2026-10-06, aproximadamente 13:56 UTC (10:56 em São Paulo)**. PID e socket de escuta conferidos; PIDs são um instantâneo e devem ser reconferidos antes de qualquer futura intervenção.

| Host | Serviço | Porta TCP | PID |
|---|---|---:|---:|
| 192.168.50.129 (lab1) | Qwen 0.5B | 19005 | 1430175 |
| 192.168.50.129 (lab1) | Qwen 1.5B | 19015 | 1430185 |
| 192.168.50.129 (lab1) | Regras Python | 19000 | 1434021 |
| 192.168.50.89 (lab2) | Qwen 0.5B | 19005 | 1436608 |
| 192.168.50.89 (lab2) | Qwen 1.5B | 19015 | 1436626 |
| 192.168.50.89 (lab2) | Regras Python | 19000 | 1441067 |
| 192.168.50.169 (lab3) | Qwen 0.5B | 19005 | 724016 |
| 192.168.50.169 (lab3) | Qwen 1.5B | 19015 | 724028 |
| 192.168.50.169 (lab3) | Regras Python | 19000 | 727970 |
| 192.168.50.54 (lab5) | Qwen 0.5B | 19005 | 828860 |
| 192.168.50.54 (lab5) | Qwen 1.5B | 19015 | 828878 |
| 192.168.50.54 (lab5) | Regras Python | 19000 | 831356 |
| 192.168.50.240 (lab7) | Qwen 0.5B | 19005 | 1434630 |
| 192.168.50.240 (lab7) | Qwen 1.5B | 19015 | 1434649 |
| 192.168.50.240 (lab7) | Regras Python | 19000 | 1438536 |
| 192.168.50.195 (lab8) | Qwen 0.5B | 19005 | 1445078 |
| 192.168.50.195 (lab8) | Qwen 1.5B | 19015 | 1445096 |
| 192.168.50.195 (lab8) | Regras Python | 19000 | 1448971 |
| 192.168.50.200 (lab6) | Regras Python | 19000 | 1437589 |
| 192.168.50.89 (lab2) | Piloto histórico Qwen 1.5B | 18089 | 1389750 |

- Campanha: diretórios `/home/caninos/smarthome_agents/study_v1/05/`, `15/` e `rules/`, com `server.pid` e `server.log`.
- Modelos: processo `/home/caninos/llama-offline/llama.cpp/build/bin/llama-server`, arquivos Qwen Q5_K_M 0.5B/1.5B, portas 19005/19015. Argumentos conferidos: `--threads 4 --threads-batch 4 --ctx-size 512 --parallel 1 --n-predict 128 --device none --metrics --no-warmup`, escuta em 0.0.0.0.
- Regras: processo `python3 rules_server_v1.py`, porta 19000. **.200 é remanescente da preparação**, fora das seis placas usadas nas campanhas finais.
- Piloto na .89: diretório `/home/caninos/smarthome_agents/single_agent_1p5b/`, processo `llama-server`, modelo `/home/caninos/models/qwen2.5-1.5b-instruct-q5_k_m.gguf`, porta 18089, contexto 1024, threads 4, parallel 1, n-predict 96.
- Na .85 (lab4), não foram encontrados serviços desse namespace nem sockets nas portas 19000/19005/19015/19050. Porta temporária19050 não estava em escuta nos oito hosts consultados.
- Serviços mantidos ativos, sem parar/reiniciar. Outros serviços e arquivos preservados. A consulta verifica processos e portas, sem inferência e sem presumir exclusividade de uso das placas.

## Próxima ação recomendada

Retomar pela leitura deste registro e de `paper/smarthome_agents/study_v1/review.md`, conferir branch/commit e alterações locais, e apreciar com os orientadores os PDFs e quatro julgamentos assistidos. **Não iniciar nova coleta nem ajustar configurações usando resultados reservados.** Após receber observações, fazer revisões editoriais autorizadas; qualquer mudança experimental exige campanha distinta, preservando as anteriores. A atividade fica pausada até nova instrução do usuário.

---

## Histórico preservado do encerramento experimental

Branch `smarthome-multiagent`; sem merge automático em main. A prévia PT foi entregue primeiro, no commit cd85d1c, e permanece intacta em `paper/smarthome_agents/preview_20261005/`. Primeiro artigo `paper/icce2027/` intacto.

Campanhas completas e preservadas:

- Desenvolvimento 1: 48 tentativas, commit1f17331.
- Desenvolvimento 2: 48 tentativas, commit72beda0; seleção compartilhada de configuração antes de observar casos reservados.
- Congelamento: commit2bab455, 18 arquivos por SHA-256; sem mudanças posteriores.
- Qualidade: 240 tentativas, 40 casos × duas repetições × três condições, commit938184b.
- Escala: 108 tentativas, 18 lotes em uma/três/seis placas, commitd2efabd, incluindo auditoria final das seis placas.

Hosts .129/.89/.169/.54/.240/.195. Ambos os modelos residentes por placa, runtime/bibliotecas e modelos idênticos, uma inferência ativa por placa, CPU4threads, contexto512, temperatura0, seeds801/802, max128, cachefalse, timeout180. Não houve colaboração ou estudo comparativo de cache. Todas as ações foram exclusivamente simuladas.

Resultados e limitações em `quality_20261006.md`, `scale_20261006.md` e manuscritos PT/EN. Regras42/80, 0.5B30/80, 1.5B12/80 na qualidade. Escala: cinco/três/uma tarefa correta por lote, respectivamente. Taxas definidas pela janela HTTP, não tempo até aplicação da ação; instrumentação afeta especialmente regras. Não representam capacidade máxima nem precisão populacional. Quatro perguntas do0.5B tiveram julgamento assistido explícito, sem atribuir sucesso, aguardando apreciação humana.

Fontes e reprodução em `paper/smarthome_agents/study_v1/README.md`; revisão de páginas e pendências em `review.md`. Autoria e ordem propostas: Hudson Moreira, Marcelo Knörich Zuffo, Laisa Costa de Biase. Afiliações/e-mails/IDs não inventados; aprovação editorial permanece dos autores. Não foram enviadas mensagens a orientadores.

Alterações anteriores não relacionadas em inventário, CHECKPOINT, modelos e logs externos ao estudo foram preservadas. Todos os ajustes de apresentação ocorrem fora das fontes congeladas. Reexecuções com mudanças futuras exigem campanha distinta, sem sobrescrever anteriores.
