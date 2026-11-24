# Ajuste do modo interativo Qwen 1,5B — 23/11/2026

## O que foi verificado

O mesmo GGUF Q5_K_M (SHA-256 `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`) foi executado no notebook x86-64, com llama.cpp compilado do commit `e25a32e98c15a1118a976685af0f4d2c1f380079`, CPU e quatro threads. A configuração original com contexto512 repetiu os erros observados nas Labradors, inclusive `no_action / Unsupported request` para “Apague a luz do quarto.”. Nos oito casos de desenvolvimento, houve1/8 sucessos, igual à campanha complementar anterior. Isso não isola todas as diferenças numéricas entre plataformas nem prova ausência de defeitos físicos; mostra que trocar a placa, sozinho, não corrigiu esse comportamento.

Instruções em português, três exemplos, contexto1024 nas SBCs e remoção dos estados das luzes da mensagem ao modelo corrigiram o comando claro testado, mas não o pedido sem cômodo (`sbc_adjusted_v1/`). No notebook, esse prompt com contexto2048 obteve5/8 nos oito casos de desenvolvimento (`x86_adjusted_v1/`), mantendo erros em ambiguidade e pedido inválido. A geração sem restrição de esquema também foi testada em `generation_probe_v1/`; não eliminou esses problemas.

Essas campanhas são exploratórias e reutilizam desenvolvimento. Não substituem os240 resultados reservados nem os108 testes de réplicas do artigo. Seus planos, pedidos, respostas e falhas estão preservados nas respectivas pastas.

## Novo modo disponível na interface

**Qwen 1,5B + regras · notebook** é um controlador híbrido, versão `hybrid_intent_v2`. Não é um modelo retreinado nem a configuração original do artigo.

- A IA classifica a intenção do pedido em ligar, apagar ou fora do escopo.
- Regras explícitas limitam o escopo às luzes da sala e do quarto, resolvem o cômodo citado, usam a localização conhecida somente quando necessária, pedem informação ausente e rejeitam conflitos.
- Pedidos fora da lista de dispositivos/termos suportados são recusados pela regra de escopo, sem inferência. Isso é identificado na tela e nos registros.
- As ações propostas ainda passam pelo executor original, que aplica alterações somente ao estado virtual.
- O controlador não recebe dados do avaliador ou respostas esperadas. Os testes usam o avaliador somente depois de produzir a ação.

A interface registra a origem de cada resposta, as saídas de intenção realmente produzidas pela IA, a ação construída pelas regras, os arquivos de cada chamada e a versão/hash do perfil. A pergunta “Em qual cômodo: sala ou quarto?” vem da regra de contexto, não é apresentada como fala gerada pelo modelo. Os modos originais nas Labradors continuam selecionáveis.

O runtime local é o serviço de usuário `smarthome-model15-local.service`, escutando somente em127.0.0.1:19119, contexto2048, quatro threads, CPU. A interface permanece em127.0.0.1:8092. O novo modo depende deste notebook ligado; a demonstração anterior no cluster e seus serviços não foram modificados. Os serviços são transitórios nesta sessão, sem habilitação automática depois de reiniciar o notebook.

## Verificação e limites

Os quatro testes direcionados de `hybrid_v2_validation/` passaram: apagar com outra formulação, priorizar o quarto explicitamente pedido sobre localização na sala, solicitar cômodo ausente e recusar ar-condicionado. O último caso foi resolvido por regra, sem chamada à IA. Isso é validação funcional de desenvolvimento, não acurácia geral de um LLM.

Cinco testes unitários verificam as regras de escopo, prioridade do cômodo, informação ausente, rotina e conflito. Os três testes anteriores de integridade/persistência das avaliações humanas continuam passando. Na versão híbrida anterior, a pergunta padronizada gerou duas pendências no avaliador conservador de texto; elas não foram convertidas em validações humanas nem removidas de seus registros. Não reivindicamos8/8 de sucesso no estudo original ou avaliação humana concluída.

O escopo é limitado: termos de iluminação suportados, sala/quarto e rotinas curtas separadas por conjunção, vírgula ou ponto e vírgula. Formulações complexas, negações e outros dispositivos precisam de avaliação adicional. Os bloqueios e a simulacão não estabelecem segurança para atuadores reais.

Compilação local conforme o procedimento geral da [documentação oficial Qwen/llama.cpp](https://qwen.readthedocs.io/en/latest/run_locally/llama.cpp.html), fixando o commit do runtime usado no experimento.

Validação final pelo navegador: “Apague a luz do quarto.” apagou somente o quarto em7,96s; “Acenda a luz.” com localização desconhecida solicitou o cômodo em7,89s. Fontes e hashes constam de `console_deployment_verification.json`. Nenhuma avaliação humana foi enviada pelo agente.
