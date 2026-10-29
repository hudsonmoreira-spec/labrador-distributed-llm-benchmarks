# Revisão editorial em resposta ao professor Bruno — 29/10/2026

Nova versão PT/EN para apreciação dos autores, baseada em `f2f566b179fcf3893099d7d1b12b888455e531ae`, na branch `smarthome-multiagent`. Não constitui aprovação do professor. As versões históricas e o artigo RPC foram preservados.

| Comentário | Correção | Local |
|---|---|---|
| Escrita maquinal e organização | Narrativa problema → comparação → método → achados → interpretação; retiradas enumerações de auditoria e repetições; resumo reescrito | Seções I–VI, ambas as línguas |
| Comandos em português no inglês | Traduções explicitamente identificadas, preservando chaves/valores técnicos; vínculo sala/living room e quarto/bedroom no método | III-A, IV-B e Tabela IV |
| Exemplos E1–E4 e IDs extensos | Tabela de quatro casos numerados com títulos descritivos, pedido/expectativa, resposta e requisito; referências LaTeX para tabela e casos | Tabela IV e IV-B |
| Legendas grandes | Cinco legendas curtas; unidades, denominadores, revisão assistida, sobreposição e janela explicados no texto | Tabelas I–V e parágrafos próximos |
| Comparação com estado da arte | Comparação metodológica explícita com HomeBench, Lu e Qin, retomada na discussão; sem ranking numérico entre estudos | II e V-A; `sources.md` |
| Final dos resultados | Síntese de formato, qualidade por categoria e atendimento por réplicas, preparando interpretação | Final de IV-C |
| Conclusão | Resposta à pergunta, achados, implicação proporcional, limite principal e próximo estudo concreto | VI |

## Exemplos e traduções

`example_mapping.json` mapeia inequivocamente os rótulos `case:paraphrase`, `case:room`, `case:clarification` e `case:preservation` (casos 1–4) aos quatro registros históricos completos, copiando os dados originais sem modificá-los e acrescentando traduções de apresentação. Textos ingleses não são novas entradas experimentais nem saídas literais do modelo. A coluna de resposta abrevia a estrutura JSON; chaves e valores técnicos são os originais. Sala corresponde a living room; quarto a bedroom.

A revisão conferiu pedidos, textos de resposta, estados e intervenção contra `analysis/failure-review-20261028/examples.json` e seus arquivos individuais. O terceiro caso mantém a formulação pouco natural do modelo também na tradução, sem transformá-la numa pergunta informativa. Os quatro julgamentos assistidos continuam pendentes; nenhum sucesso foi acrescentado. Validação automática da correspondência não substitui validação humana da tradução ou do significado.

## Integridade e reprodução

Snapshot científico preservado: `a834b8255f736fb59425b146be183c17866a2c7d`. A análise complementar citada no manuscrito aponta ao commit anterior completo `f2f566b179fcf3893099d7d1b12b888455e531ae`, que já contém todos os seus dados. Não há hash do próprio PDF inserido dentro dele. Protocolo, dados, modelos, avaliador, julgamentos, geradores e arquivos históricos `generated/` e `failure_analysis/` não foram alterados. Os novos denominadores de apresentação são conferidos contra o CSV complementar.

Os verificadores históricos continuam cobrindo suas respectivas evidências e arquivos gerados originais. A checagem adicional desta revisão verifica os insumos efetivamente incluídos no novo manuscrito e os mapeamentos traduzidos. Ela não substitui os verificadores científicos nem julga qualidade de tradução.

Da raiz do repositório:

```bash
python3 experiments/smarthome_agents/scripts/verify_submission_artifact.py --output /tmp/scientific-audit.json
python3 experiments/smarthome_agents/scripts/verify_failure_review.py --output /tmp/failure-audit.json
python3 paper/smarthome_agents/study_v1/editorial_20261029/verify_editorial.py
cd paper/smarthome_agents/study_v1
latexmk -pdf -interaction=nonstopmode -halt-on-error main_en.tex main_pt.tex
```

Relatórios de execução e conferência dos PDFs estão neste diretório. Todas as páginas PT/EN foram renderizadas e inspecionadas. Fontes, margens e tamanho de página IEEE foram preservados; somente o espaçamento interno de duas tabelas foi ajustado para acomodar cabeçalhos legíveis, sem reduzir fontes ou usar espaçamento negativo. Os exemplos usam fonte de 9 pt, maior que os 8 pt das tabelas numéricas históricas. As restrições oficiais consultadas estão em `sources.md`.

Permanecem: apreciação editorial e linguística pelos autores, validação humana dos quatro julgamentos, conferência humana das traduções, escolha de eventual rota de quatro páginas e contato de Pablo para cadastro. Submissão ICCE/EDAS continua dependendo de instrução específica; nenhuma submissão foi realizada. Não houve novas campanhas, acesso às placas, merge em main ou force push. Alterações locais de inventário e arquivos alheios foram excluídos do commit.
