# Encerramento do escopo reduzido — 2026-10-06

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
