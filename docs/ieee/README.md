# Material suplementar para publicação IEEE

Esta pasta define a apresentação do artefato experimental, sem inventar resultados que ainda não foram medidos. A estrutura segue uma sequência familiar a leitores de artigos experimentais: objetivo, protocolo, ambiente, dados, reprodução, limitações e evidências.

## Correspondência com um artigo

| Seção do artigo | Evidência neste repositório |
|---|---|
| Ambiente experimental | `research/reports/inventory_report.md` e `research/data/inventory.csv` |
| Método de descoberta | `research/scripts/discover.sh` |
| Diagnósticos | `research/scripts/diagnostics.sh` e `research/data/runs/*/diagnostics/` |
| Seleção da bancada | `research/reports/selection.md` |
| Protocolo planejado | `research/reports/pilot_1_2.md` |
| Tratamento de falhas | `research/reports/contingency.md` |
| Evidência primária | `research/data/runs/*/hosts/*/raw.txt` |

O relatório de inventário deve ser citado como caracterização do ambiente, não como resultado de desempenho. Resultados de throughput, latência, consumo, escalabilidade ou qualidade só devem ser adicionados depois de uma execução experimental explicitamente identificada.

## Convenções recomendadas

- registrar todos os horários em UTC;
- associar cada resultado ao commit do código, ao hash do modelo, à quantização, aos parâmetros e ao identificador da execução;
- distinguir claramente configuração, observação, métrica derivada e interpretação;
- preservar logs primários e gerar tabelas/figuras por scripts versionados;
- declarar falhas, exclusões e nós substituídos, sem substituir evidências silenciosamente.
