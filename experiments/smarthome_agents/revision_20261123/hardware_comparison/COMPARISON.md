# Comparação de hardware — Qwen 1,5B original

O modelo original foi executado novamente no notebook, sem o controlador híbrido. Cada requisição JSON foi copiada dos registros SBC, preservando exatamente os bytes do arquivo e verificando seu SHA-256 antes de enviar.

| Medida | Labradors (registros anteriores) | Notebook (nova execução) |
|---|---|---|
| Casos de desenvolvimento | 8 | 8 |
| Sucesso pelo avaliador original | 1/8 | 1/8 |
| Mediana HTTP | 78.48 s | 9.48 s |

As oito respostas foram idênticas, caractere por caractere e como JSON (8/8). O notebook teve mediana de resposta aproximadamente 8.3 vezes menor neste conjunto.

## Controle da configuração

Mesmo arquivo Qwen2.5-1.5B-Instruct Q5_K_M (SHA-256 b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c); mesma versão llama.cpp b9584/e25a32e98; quatro threads de computação e lote; contexto512; um slot; CPU; temperature0; seed801; max_tokens128; cache_promptfalse; prompt original e esquema JSON originais. Nenhuma saída foi corrigida por regras no teste da resposta do modelo. O executor/evaluador original foi usado depois da geração para conferir o resultado.

## Pares

| Comando | Host SBC | Resultado nos dois ambientes | SBC (s) | PC (s) | Resposta idêntica |
|---|---|---|---|---|---|
| Acenda a luz da sala. | 192.168.50.129 | Incorreto | 79.62 | 9.34 | Sim |
| Apague a luz do quarto. | 192.168.50.89 | Incorreto | 60.12 | 7.08 | Sim |
| Pode deixar a sala iluminada? | 192.168.50.169 | Incorreto | 79.43 | 10.13 | Sim |
| Acenda a luz. | 192.168.50.240 | Incorreto | 77.88 | 10.15 | Sim |
| Acenda a luz da sala e apague a luz do quarto. | 192.168.50.89 | Correto | 80.84 | 9.62 | Sim |
| Acenda a luz. | 192.168.50.129 | Incorreto | 76.85 | 8.90 | Sim |
| Apague a luz, por favor. | 192.168.50.89 | Incorreto | 61.63 | 8.94 | Sim |
| Ligue o ar-condicionado da sala. | 192.168.50.169 | Incorreto | 79.09 | 9.72 | Sim |

## Interpretação

Nestes oito casos e nesta configuração, trocar a Labrador pelo notebook alterou o tempo de resposta, mas não alterou a qualidade nem o texto gerado. Isso enfraquece a hipótese de uma falha física específica das placas como explicação desses erros. O resultado é compatível com erros da combinação modelo/prompt/configuração, que precisam ser investigados separadamente.

A conclusão não é um certificado de integridade física, nem uma demonstração de que hardware nunca influencia inferência. Há somente oito casos de desenvolvimento, uma nova repetição no notebook, baseline SBC coletado anteriormente em vários hosts, compiladores/arquiteturas diferentes e medição HTTP com Ethernet nas SBCs e loopback no PC. Não foram isolados energia, temperatura, kernels ou todas as combinações de backend. O tamanho pequeno e desenvolvimento reutilizado impedem generalização estatística.

## Evidências e uso

`pc_exact_replay_v1/plan_before_dispatch.json` contém os hashes dos arquivos, a configuração, CPU do notebook, ordem dos casos e limitações, registrados antes da nova geração. Cada pasta de caso contém a requisição copiada, resposta bruta e comparação. `summary.json` e `pairs.csv` consolidam os pares. Os dados e métricas originais do artigo permanecem preservados.

Na interface local, a opção **Qwen1,5B original · notebook** permite repetir manualmente o teste puro. **Qwen1,5B · original na Labrador** usa a placa; **Qwen1,5B + regras · notebook** continua sendo um modo híbrido diferente e não participa desta comparação. O runtime puro está no serviço de usuário `smarthome-model15-pc-original.service`, porta127.0.0.1:19118, sem publicação externa nem inicialização automática após reiniciar o notebook.
