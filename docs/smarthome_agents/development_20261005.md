# Desenvolvimento do escopo reduzido — 2026-10-05

Primeira campanha compacta: `experiments/smarthome_agents/runs/20261005-study-v1-development/`, 8 casos × 2 repetições × 3 condições = 48 tentativas. Todas preservadas, 48 execuções completas, 48 respostas válidas, zero cache reportado. A análise reconstruiu propostas, bloqueios e estados diretamente dos arquivos individuais e conferiu o conteúdo contra as respostas HTTP brutas.

| Condição | Sucessos / 16 | Mediana (s) | p95 (s), n=16 | Propostas indevidas | Bloqueadas |
|---|---:|---:|---:|---:|---:|
| Regras | 12 | 0,053 | 0,418 | 0 | 0 |
| Qwen 0.5B | 2 | 32,688 | 43,244 | 14 | 4 |
| Qwen 1.5B | 4 | 93,128 | 141,646 | 12 | 4 |

Esses resultados são de desenvolvimento e não estimam precisão geral. `analysis/development-1/` contém tabelas por cenário e categorias. Dez propostas indevidas do 0.5B e oito do 1.5B foram aplicadas somente no simulador. O executor permitiu que erros chegassem ao avaliador independente; quatro propostas por modelo foram bloqueadas pela política geral de falta de informação de local.

## Ajuste autorizado antes de congelar

O prompt compacto inicial em português citava planos de rotina e as respostas frequentemente propunham alterar luzes não solicitadas ou reproduziam o estado visível como decisão. A próxima campanha de desenvolvimento explicitará, em instruções gerais, que somente luzes solicitadas devem mudar e que uma ação simples e um plano têm usos distintos. Não haverá exemplos com a resposta de qualquer cenário. Temperatura, limite de tokens, esquema, quantização, runtime e política permanecem iguais.

A regra finita será ajustada para remover a fórmula de cortesia `por favor` das extremidades do pedido, observada no caso de desenvolvimento dev2-07. Isso não introduz interpretações de paráfrases desconhecidas nem consulta o gabarito. Ajustes são registrados em nova campanha; nenhuma execução reservada ocorreu.

## Infraestrutura e limites

Hosts finais .129/.89/.169/.54/.240/.195. Auditoria de binário, todas as bibliotecas `.so`, modelos e arquivos de regras passou nos seis hosts. Processos, propriedades e comandos preservados em `runs/20261005-study-v1-audit/`. Serviços residentes antigos ficam registrados; não se afirma exclusividade de memória da placa. A comparação de qualidade distribui cada modelo por todos os hosts, e a análise posterior deve mostrar latência por host para expor variação.

A preparação .85 sofreu conexões fechadas; a cópia notebook→.200 foi muito lenta e não integra o conjunto final. A transferência direta .89→.54 do 0.5B durou 44,743 s. Servidor temporário de arquivos encerrado. Preparações e recuperação do reinício do Codex são evidência operacional, distintas das tentativas de inferência.
