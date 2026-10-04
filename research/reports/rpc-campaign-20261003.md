# Evidências da campanha RPC — 2026-10-03

## Resultado principal

Na bancada homogênea, o cliente local conseguiu carregar e executar o Qwen2.5-1.5B-Instruct Q5_K_M com 2, 4 e 6 servidores RPC. Com 8 servidores, o cliente permaneceu em `Loading model...` e foi encerrado no ensaio confirmatório de 90 s (`exit 124`). Esse ensaio não é diretamente comparável aos casos concluídos em aproximadamente 128 s e não permite declarar um limite do RPC.

| Hosts RPC | Resultado | Tempo real | Evidência de saída |
|---:|---|---:|---|
| 2 | sucesso | 127,74 s | resposta `Hello`, `command_exit=0` |
| 4 | sucesso | 127,84 s | resposta `Hello`, `command_exit=0` |
| 6 | sucesso | 128,02 s | resposta `Hello`, `command_exit=0` |
| 8 | timeout | 90,05 s no ensaio confirmatório | sem resposta; `command_exit=124` |

Os tempos são de uma execução curta (`prompt=Hi.`, um token, contexto 512, quatro threads e `-ngl 99`). A linha exibida pelo cliente foi `Prompt: 1.2 t/s | Generation: 0.0 t/s`; como a geração foi limitada a um token, essa métrica não é adequada para concluir desempenho sustentado.

## Método reproduzível

- Cliente: `llama-cli` local, commit `68e79bd8cd6b7995f8fce8da252b249bbf237e63`, compilado com suporte RPC e limite de backends ampliado para acomodar os backends remotos e o CPU local.
- Modelo: `qwen2.5-1.5b-instruct-q5_k_m.gguf`, SHA-256 `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`.
- Servidores: `ggml-rpc-server` na porta TCP 50052, nos hosts `192.168.50.42`, `.118`, `.231`, `.74`, `.44`, `.75`, `.71` e `.241`; os snapshots registraram a porta como `listening` antes e depois dos casos concluídos.
- Parâmetros: `-ngl 99 -c 512 -t 4 -n 1 -p 'Hi.' --no-display-prompt`.
- Cada caso foi executado sequencialmente, com registro de log, tempo, código de saída e snapshot de memória/estado da porta.

O procedimento automatizado está em [rpc_campaign.sh](../scripts/rpc_campaign.sh). Os artefatos brutos estão no diretório [rpc-campaign](../data/runs/20261003T-campaign-rpc-1/rpc-campaign), começando pelo [manifest.txt](../data/runs/20261003T-campaign-rpc-1/rpc-campaign/manifest.txt), além dos logs individuais de 2, 4, 6 e 8 hosts.

## Interpretação para o artigo

O resultado sustenta três afirmações defensáveis:

1. A instalação e a comunicação RPC funcionam de ponta a ponta com o modelo de 1,5B.
2. A execução permanece funcional até 6 servidores na configuração avaliada.
3. Adicionar o oitavo servidor não produziu uma execução concluída dentro do limite operacional definido; o problema aparece durante o carregamento, não como erro de inferência retornado ao usuário.

Não se deve afirmar, com estes dados, que mais hosts sempre reduzem o tempo ou que o RPC suporta no máximo seis hosts. Os tempos de 2/4/6 são praticamente iguais, o que indica que o ensaio mede sobretudo carregamento, sincronização e overhead distribuído, e não escalabilidade de geração. Também é necessário repetir cada ponto várias vezes e incluir uma linha de base local antes de calcular média, desvio-padrão, taxa de sucesso e intervalo de confiança.

## Próxima etapa recomendada

Repetir 1, 2, 4, 6 e 8 hosts em pelo menos cinco repetições por ponto, usando um prompt que gere 64–128 tokens e separando tempo de carregamento de tempo de geração. Em paralelo, coletar CPU, memória, tráfego e logs do RPC. Isso permitirá distinguir limite de memória/carregamento de overhead de agendamento e produzir uma curva de escalabilidade publicável.
