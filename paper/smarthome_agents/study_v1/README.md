# Estudo de controle doméstico simulado — candidato ICCE 2027

Fontes IEEE de conferência: `main_en.tex` (inglês) e `main_pt.tex` (português). A prévia inicial fica preservada em `../preview_20261005/`; o primeiro artigo permanece em `paper/icce2027/`.

O protocolo e seus critérios estão congelados em `experiments/smarthome_agents/study_v1/freeze.json` (commit `2bab455`, código `72beda0`). A reconstrução exige registros completos; não usar arquivos parciais para apresentar resultados finais. Dados confirmados de autoria e situação da preparação em `review.md`. O artigo RPC é separado.

**Revisão de 2026-10-20 (histórica):** versões inglesa e portuguesa revisadas, então com quatro páginas cada; seis autores USP e contato correspondente confirmados; sem financiamento. [Relatório técnico](submission/technical-review-20261020.md), [campos para EDAS](submission/edas-draft.md) e [auditoria pública](artifact/README.md). Não cadastrar nem enviar ao ICCE/EDAS sem nova instrução do usuário.

Reprodução a partir da raiz, após concluir qualidade e escala:

```bash
python3 experiments/smarthome_agents/scripts/analyze_study_v1.py --run experiments/smarthome_agents/runs/20261006-study-v1-quality --out experiments/smarthome_agents/analysis/quality-v1
python3 experiments/smarthome_agents/scripts/analyze_action_steps_v1.py --run experiments/smarthome_agents/runs/20261006-study-v1-quality --out experiments/smarthome_agents/analysis/quality-v1
python3 experiments/smarthome_agents/scripts/analyze_study_v1.py --run experiments/smarthome_agents/runs/20261006-study-v1-scale --out experiments/smarthome_agents/analysis/scale-v1
python3 experiments/smarthome_agents/scripts/analyze_action_steps_v1.py --run experiments/smarthome_agents/runs/20261006-study-v1-scale --out experiments/smarthome_agents/analysis/scale-v1
python3 experiments/smarthome_agents/scripts/make_study_assets.py --quality experiments/smarthome_agents/analysis/quality-v1 --scale experiments/smarthome_agents/analysis/scale-v1 --out paper/smarthome_agents/study_v1/generated --protocol-commit 2bab455 --data-commit d2efabd --date 2026-10-06
cd paper/smarthome_agents/study_v1/generated
latexmk -pdf -interaction=nonstopmode -halt-on-error quality_figure.tex scale_figure.tex quality_figure_pt.tex scale_figure_pt.tex
cd ..
latexmk -pdf -interaction=nonstopmode -halt-on-error main_en.tex main_pt.tex
```

Os CSVs preservam contagens por tentativa, cenário, categoria e host, latência mediana/p95 com n, tokens, RSS e VmHWM de processo. `manual_reviews.json` mantém revisões caso a caso separadas das respostas brutas. `action_steps.csv` conta comandos; o diagnóstico congelado por resposta de plano pode incluir omissões, conforme `action_units.md`.

Lotes de escala registram cada janela e taxas de respostas e tarefas corretas por minuto. Não são um teste de saturação nem capacidade máxima. Dois servidores de modelo ficam residentes em cada placa, com uma inferência ativa por placa; RSS não é memória exclusiva. Critérios, prompts e política não são reajustados a partir dos resultados reservados.

Nenhum PDF de terceiro é redistribuído. Bibliografia e links oficiais estão em `references.bib`; notas de leitura e identidade dos modelos em `experiments/smarthome_agents/study_v1/model-provenance.md`. Os hashes dos modelos coincidem com os arquivos GGUF oficiais da Qwen.

Verificação completa sem acesso a placas, sem nova inferência e sem alterar dados-fonte:

```bash
python3 experiments/smarthome_agents/scripts/verify_submission_artifact.py --output /tmp/smarthome-audit.json
```

O verificador compara os insumos com o snapshot científico imutável e reconstrói as análises em diretório temporário. Os parâmetros opcionais de proveniência do gerador permitem reconstrução sem metadados Git e não modificam medições, avaliação ou critérios.


## Revisão de falhas — 2026-10-28

Versões atuais PT/EN: cinco páginas cada, formato IEEE conference US Letter, sem reduzir fontes ou margens. A [diretriz oficial](https://icce.org/2027/submission-guidelines/) permite até seis páginas na submissão inicial; quatro páginas são o limite condicional para a rota de Transactions/periódicos associados. A escolha dessa rota ainda exigiria condensar o texto. A revisão anterior permanece no histórico Git (commit anterior `365847f`); a prévia e o artigo RPC não foram alterados.

A observação do professor foi atendida com critérios explícitos, tabela de requisitos reprovados por tentativa e quatro exemplos reais cobrindo as três condições. [Relatório e decomposição](../../../experiments/smarthome_agents/analysis/failure-review-20261028/README.md), [revisão editorial](submission/failure-review-20261028.md) e [notas da referência](reading-notes.md). As contagens se sobrepõem; não somar linhas para obter total de insucessos. Os quatro julgamentos assistidos continuam provisórios.

O novo script é complementar e também gera as tabelas/textos PT/EN em `failure_analysis/`; não modifica o gerador histórico, os 18 arquivos congelados ou as análises `quality-v1`/`scale-v1`. O snapshot científico continua `a834b8255f736fb59425b146be183c17866a2c7d`. Os novos arquivos são publicados separadamente nesta branch.

Reprodução da revisão, a partir da raiz (somente dados existentes):

```bash
python3 experiments/smarthome_agents/scripts/verify_submission_artifact.py --output /tmp/smarthome-audit.json
python3 experiments/smarthome_agents/scripts/analyze_failure_criteria.py
python3 experiments/smarthome_agents/scripts/verify_failure_review.py --output /tmp/smarthome-failure-audit.json
cd paper/smarthome_agents/study_v1
latexmk -pdf -interaction=nonstopmode -halt-on-error main_en.tex main_pt.tex
```

Os comandos históricos acima reconstroem as análises originais; para apenas conferi-las sem sobrescrever arquivos, prefira o verificador offline, que usa diretório temporário. A conferência complementar também compara byte a byte seus novos CSV/JSON/TeX em diretório temporário. Não contata placas, não usa pesos locais e não executa inferência.
