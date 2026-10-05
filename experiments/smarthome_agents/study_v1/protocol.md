# Protocolo reduzido candidato — study_v1

Só estará congelado quando `freeze.json` for registrado após a campanha de desenvolvimento. Não usar resultados reservados para escolher configurações.

## Pergunta e condições

Referência de regras finitas; Qwen2.5-0.5B-Instruct Q5_K_M; Qwen2.5-1.5B-Instruct Q5_K_M. Nenhuma colaboração entre agentes. Casa simulada com sala/quarto, luzes on/off, ações simples, uma rotina de duas ações explícitas, esclarecimento de local e pedidos inválidos. O coordenador aplica apenas mudanças em dicionários Python.

Seis Labradores selecionadas: lab1 (.129), lab2 (.89), lab3 (.169), lab5 (.54), lab7 (.240), lab8 (.195). Quatro CPUs ARM64, Debian 12, ~2 GB RAM. Registrar inventário exato, runtime e bibliotecas por hash e hashes dos modelos. Usar o mesmo runtime b9584-e25a32e98, quatro threads e quatro threads de lote, contexto 512, uma vaga por servidor, CPU (`--device none`), processos residentes. O modelo 0.5B usa porta 19005; 1.5B porta 19015; regras Python porta 19000. Serviços anteriores ficam preservados; seus processos/memória/carga são registrados. Instantes anteriores/posteriores não medem pico por requisição.

## Desenvolvimento

Oito casos em `development.json`, duas repetições por condição, seeds 801 e 802. Instrução geral compacta em inglês e pedidos em português; estado contém somente luzes e localização conhecida. Saída com esquema de uma ação ou plano de até dois passos, JSON estrito; temperatura zero, 128 tokens, cache_prompt false, timeout 180 s. Modelos comparados apenas nesses casos para verificar viabilidade. Nenhuma exigência de sucesso mínimo que induza descarte de erros do modelo.

## Conjunto reservado e critérios

40 casos distintos em `reserved.json`: oito claros, oito paráfrases, oito rotinas, oito ambiguidades e oito inválidos. Cenários produzidos neste projeto em português; não são uma amostra aleatória de residências nem uma implementação do HomeBench. Duas repetições por caso/condição, em hosts distintos, preservadas separadamente. As repetições medem estabilidade operacional; temperatura zero limita diversidade.

Uma proposta de um passo pode usar set_light ou um plano de um passo: a equivalência é julgada pelos passos, sem penalizar esse invólucro. Sucesso exige transporte completo, geração stop, JSON válido, proposta correta, estado final esperado e estados preservados. Planos precisam conter exatamente os passos previstos (ordem indiferente), sem passo extra. Pedidos inválidos exigem no_action e nenhuma mudança. Ambiguidades exigem ask_clarification para room, pergunta que solicite o local ausente e estado preservado. Perguntas fora das formas conservadoras são revisadas manualmente com decisão e justificativa anexadas. Nunca contar pendência como sucesso. A presença lexical de cômodo/ambiente é insuficiente.

Política geral de bloqueio em `docs/smarthome_agents/policy_v1.md`: desconhecimento de cômodo ou permissão inválida bloqueiam execução; falta de qualquer nome de cômodo no pedido e de localização válida bloqueia propostas de iluminação. A política não julga se o cômodo proposto é o correto. O executor recebe somente pedido, estado e permissões. Gabarito usado exclusivamente na análise. Registrar propostas indevidas, bloqueadas e aplicadas, além de erros de formato e operação.

## Distribuição e medição

Qualidade: 40 × 2 × 3 = 240 tentativas, distribuídas por índice `(cenário + 3*repetição + 2*condição) mod 6`, com fila sequencial por host e intercalamento por cenário. Todos os hosts atendem as três condições. Nenhum host executa duas inferências simultâneas. Cache desativado; registrar cache_n e cached_tokens para verificar. Sem estudo de cache nesta campanha. Cada pedido reconstrói o estado inicial e não recebe histórico de outros pedidos. Servidor de regras é sem estado. Preservar payload e resposta brutos.

Latência: relógio monotônico no coordenador, envio até leitura/decodificação da resposta HTTP. A medição inclui rede e inferência, sem inicialização do modelo, sem SSH de coleta de memória. Baseline de regras também usa HTTP na Labrador. Tokens e tempos de prompt/geração são reportados pelo runtime; regras não têm tokens de modelo (não registrar zero como medida comparável de tokens). RSS antes/depois e VmHWM do processo desde sua inicialização são separados: VmHWM não é pico individual da tentativa. Instantâneos registram processos concorrentes e carga; nenhuma inferência adicional é disparada em servidores anteriores pelo controlador.

Escala: para cada condição, 1, 3 e 6 réplicas, duas repetições. Lote fixo de seis casos reservados, índices 0,8,16,24,32,17: um claro, uma paráfrase, duas rotinas, uma ambiguidade e um inválido. Cada réplica atende um pedido por onda; todas partem de estados independentes. Mesma quantidade de trabalho (seis pedidos) em cada tamanho. Janela = primeiro envio até última resposta; inclui intervalos de preparação/medição entre ondas. Registrar também esses intervalos, latência individual, respostas/min e tarefas corretas/min. Não afirmar capacidade máxima/saturação a partir deste lote fechado. Alternar hosts por repetição. Regras têm mesmas ondas e instrumentação, cujos custos podem dominar sua vazão.

Não comparar diretamente p95 de tamanhos de amostra diferentes sem indicar n. P95 por posto mais próximo: sorted[ceil(.95*n)-1]. Mediana por requisição e por cenário; sucesso por cenário = média das duas repetições; média por categoria agrupa esses cenários. Não usar repetições como 80 casos independentes. Sem teste de significância ou intervalo de precisão populacional neste conjunto elaborado.

## Preservação e término

Nenhuma tentativa excluída por falha. Sem retries silenciosos, sem substituição de respostas. Interrupção de campanha deve deixar início/payload e ser reportada; retomada ou correção usa nova campanha. Congelamento inclui scripts executores, conjunto, esquema, prompts, política, parâmetros e métodos. Após congelar, mudanças exigem outro identificador. Concluir após registros previstos, conferência, scripts de análise e PDFs inglês/português revisados. Preservar prévia e primeiro artigo.
