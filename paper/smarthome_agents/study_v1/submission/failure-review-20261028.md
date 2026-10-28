# Revisão editorial: em que cada abordagem falhou — 2026-10-28

## Escopo, preservação e conferência inicial

Trabalho realizado na branch `smarthome-multiagent`, a partir de `365847f` (último commit: correção dos hyperlinks imutáveis). Foram lidos os manuscritos PT/EN, protocolo/manifesto, política, notas, relatórios e código de avaliação/análise. Não houve nova inferência, acesso às placas, campanha, ajuste dos modelos, reclassificação de sucesso ou alteração dos critérios.

As modificações locais anteriores em `research/data/inventory.csv`, `inventory.json` e `research/reports/inventory_report.md`, bem como CHECKPOINT, modelos, script externo e logs não rastreados, foram preservadas e excluídas do commit. O artigo RPC em `paper/icce2027/`, a prévia em `paper/smarthome_agents/preview_20261005/` e todas as versões históricas permanecem preservados. Não houve merge em main. A versão anterior dos manuscritos atuais continua disponível em `365847f`.

## Resposta à observação do professor

A seção de critérios agora explicita o caráter conjuntivo do sucesso: conclusão normal, formato válido, ação/passos corretos, estado-alvo, preservação, esclarecimento informativo, rejeição de inválidos e ausência de passos extras/proibidos. Distingue falha operacional, falha de formato, falha semântica/de decisão e intervenção do executor. Bloqueio não corrige a proposta; `no_action` depende do pedido.

A tabela de categorias apresenta as cinco categorias em ordem conceitual e informa oito cenários com duas repetições por condição, sem independência artificial das 16 tentativas. O asterisco identifica a pendência assistida no 0.5B/ambiguidade. A nova tabela de falhas complementa essa comparação com requisitos reprovados e denominadores aplicáveis, não com “causas principais”.

As contagens foram reconstruídas de todos os `summary.json` e respostas HTTP individuais, conferindo parsing, estado, permissão, avaliação e ledger. Os arquivos históricos attempts/categories/failure_inventory/action_steps/action_summary/metrics foram usados como referências de coerência, sem sobrescrevê-los. Os totais permanecem 80 tentativas/40 cenários por condição, com 42/30/12 sucessos automáticos. A ausência de falhas operacionais e de formato é conferida, não presumida a partir de verificações ausentes.

A decomposição completa está em [README da análise](../../../../experiments/smarthome_agents/analysis/failure-review-20261028/README.md), [CSV por condição](../../../../experiments/smarthome_agents/analysis/failure-review-20261028/criteria_by_condition.csv), [CSV por tentativa/critério](../../../../experiments/smarthome_agents/analysis/failure-review-20261028/criteria_by_attempt.csv) e [JSON com verificações originais](../../../../experiments/smarthome_agents/analysis/failure-review-20261028/attempts.json). As tabelas numéricas são geradas, não transcritas neste relatório.

## Mapeamento e interpretação

`analyze_failure_criteria.py` é um script novo, fora do manifesto congelado. Reutiliza o avaliador apenas para conferir igualdade com o registro, sem alterar o resultado. A agregação posterior é documentada em `summary.json` e no README: seletores terminados em `:` usam prefixo; os demais usam igualdade exata. Cada grupo conta no máximo uma vez por tentativa; qualquer verificação reprovada reprova o grupo. Nenhuma correspondência resulta em `absent`, não em aprovação. Os campos explícitos de conclusão e formato são tratados separadamente das verificações condicionais do avaliador.

- `expected_action` só é imposto pelo código para esclarecimento/rejeição. Ações simples e planos de um passo são comparados por igualdade dos passos, sem penalizar invólucros.
- `final:` examina valores-alvo; `unchanged:` examina preservação. Várias luzes reprovadas não multiplicam a tentativa.
- `prohibited:` é uma verificação histórica no objeto de topo; `no_prohibited_plan_steps` examina também passos dentro de planos. A união evita ignorar planos ou contar duas vezes a mesma tentativa. Mesmo quando a lista de proibições é vazia, esse último check está presente; aprovação nesse caso não comprova desempenho em um desafio de rejeição.
- Esclarecimento e `no_action` são verificados condicionalmente à proposta. O número de propostas e acertos acompanha as contagens: ausência de esclarecimentos no 1.5B não é capacidade demonstrada.
- Bloqueio é por resposta/plano; o plano é atômico. A contagem de comandos permanece separada da contagem de tentativas. O novo script reconstrói e compara cada linha de comandos contra a análise histórica, incluindo comandos corretos, indevidos, bloqueados e simulados.

Há 146 tentativas com mais de um grupo reprovado. Não somar linhas nem interpretar verificações correlacionadas como mecanismos causais independentes. A união dos grupos malsucedidos coincide com o conjunto original de tentativas malsucedidas.

## Exemplos reais incluídos nas duas línguas

Os quatro exemplos são ilustrativos, não substituem as contagens. Texto original em português mantido, com notação abreviada de campos JSON identificada. [examples.json](../../../../experiments/smarthome_agents/analysis/failure-review-20261028/examples.json) contém requisição, saída literal integral, estados, gabarito congelado, intervenção, falhas e caminhos para os arquivos originais:

1. `rules-held-paraphrase-01-rep1-169`: pedido válido fora da gramática, resposta `no_action`, luz solicitada permanece desligada.
2. `05-held-ambiguity-01-rep1-169`: seleciona sala sem informação de cômodo; proposta bloqueada; preservação não transforma a tentativa em sucesso.
3. `05-held-ambiguity-03-rep1-240`: `ask_clarification` com “Quero a luz acender.”; julgamento assistido provisório por não solicitar o cômodo. Nenhuma validação humana nova.
4. `15-held-clear-01-rep1-240`: atende sala, mas inclui desligar quarto; plano permitido no simulador, estado-alvo correto, preservação e passos exatos reprovados. Uma resposta com dois comandos, um extra.

## Julgamentos assistidos

Os quatro registros originais de Codex continuam `human_validation_pending=true`. A tabela de categorias, a linha de esclarecimentos e o texto de sensibilidade tornam isso visível. Nenhum novo sucesso foi atribuído. Aceitar todos mudaria apenas a hipótese de sensibilidade: 0.5B de 30/80 para 34/80, ambiguidade de 0/16 para 4/16 e esclarecimentos reprovados de 12/12 para 8/12. O código não aplica essa hipótese como resultado.

## Referência incorporada e alcance

Qin et al., *Empirical Guidelines for Deploying LLMs onto Resource-constrained Edge Devices*, ACM TODAES 30(5), artigo 70, 2025, [DOI 10.1145/3736721](https://doi.org/10.1145/3736721), foi incorporado ao BibTeX e à introdução. A discussão conecta a escolha conjunta de modelo, tarefa e recursos aos limites do presente estudo. A comparação é com seleção/personalização sob restrições, não uma replicação ou confirmação causal a partir do ranking 0.5B/1.5B. LoRA, RAG e especialização são possibilidades futuras, não recursos implementados.

As [notas de leitura](../reading-notes.md) registram metadados completos, fontes e limite de acesso: ACM respondeu 403 diretamente, mas havia texto indexado; o preprint dos autores foi lido e os metadados/resumo publicado foram conferidos no registro institucional. Não foi presumida identidade integral entre preprint e versão final, nem reproduzido PDF de terceiros. As afirmações usadas estão sustentadas também no resumo publicado.

## Artefatos, equivalência e reprodução

O snapshot científico citado continua `a834b8255f736fb59425b146be183c17866a2c7d`. O complemento posterior tem manifesto com 498 insumos, todos conferidos também contra o manifesto original; não é atribuído retroativamente ao snapshot. O link no artigo distingue a branch com o complemento da evidência científica imutável.

O gerador histórico e suas tabelas/figuras permanecem intactos. O novo script gera análises em `analysis/failure-review-20261028/` e dez arquivos TeX em `failure_analysis/`, incluindo categorias, falhas, padrões, esclarecimentos e exemplos em ambas as línguas. O gráfico redundante de sucesso agregado deixou de ser inserido nos PDFs atuais; suas fontes e arquivos históricos foram preservados. A figura de replicação permanece.

A equivalência PT/EN foi revisada editorialmente quanto a critérios, padrões, exemplos, cautelas, referência e limites. O verificador compara números, citações, fontes TeX e trechos literais dos exemplos entre línguas. Não se apresenta essa checagem automática como prova geral de equivalência de tradução.

Comandos a partir da raiz:

```bash
python3 experiments/smarthome_agents/scripts/verify_submission_artifact.py --output /tmp/smarthome-audit.json
python3 experiments/smarthome_agents/scripts/analyze_failure_criteria.py
python3 experiments/smarthome_agents/scripts/verify_failure_review.py --output /tmp/smarthome-failure-audit.json
cd paper/smarthome_agents/study_v1
latexmk -pdf -interaction=nonstopmode -halt-on-error main_en.tex main_pt.tex
```

[Auditoria científica](scientific-audit-20261028.json): 3.021 hashes, 18 arquivos congelados, 27 análises e 19 fontes/resumos históricos reconstruídos byte a byte, 240 tentativas de qualidade, 108 de replicação, 18 janelas de lote. [Auditoria complementar](failure-audit-20261028.json): 498 hashes, 18 arquivos gerados determinísticos, 2.400 registros de tentativa/critério sem duplicação, quatro exemplos fiéis e nenhum sucesso novo. A reconstrução usa diretório temporário nos verificadores e não contata placas.

## PDFs e decisões humanas remanescentes

Ambos os PDFs atuais têm cinco páginas, IEEE conference US Letter, com as mesmas fontes e margens do template. Não se reduziu tamanho de letra/margem nem se usou espaçamento negativo para acomodar conteúdo. A [diretriz oficial consultada em 28/10](https://icce.org/2027/submission-guidelines/) permite até seis páginas inicialmente; o limite de quatro páginas é condicional à rota de Transactions/periódicos associados. Essa rota exigiria condensação editorial futura, caso escolhida.

Os dez renderizados foram inspecionados quanto a tabelas, figura, referências, margens e quebras; a conferência objetiva de PDFs e hyperlinks é registrada em `pdf-check-20261028.json`. Autoria/ordem, USP, correspondente, financiamento e limites científicos foram preservados. Nenhum registro ou envio foi feito ao ICCE/EDAS.

Permanecem decisões humanas: validar especificamente os quatro julgamentos semânticos assistidos; apreciar a revisão editorial; escolher eventual rota de periódico e condensação para quatro páginas; fornecer e-mail de Pablo para cadastro e autorizar submissão quando desejado. Nada disso foi presumido concluído pela publicação autorizada desta revisão no GitHub.
