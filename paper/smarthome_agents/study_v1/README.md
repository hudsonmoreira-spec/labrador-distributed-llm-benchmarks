# Estudo de controle doméstico simulado — candidato ICCE 2027

Fontes IEEE de conferência: `main_en.tex` (inglês) e `main_pt.tex` (português). A prévia inicial fica preservada em `../preview_20261005/`; o primeiro artigo permanece em `paper/icce2027/`.

O protocolo e seus critérios estão congelados em `experiments/smarthome_agents/study_v1/freeze.json` (commit `2bab455`, código `72beda0`). A reconstrução exige registros completos; não usar arquivos parciais para apresentar resultados finais. Dados confirmados de autoria e situação da preparação em `review.md`. O artigo RPC é separado.

**Revisão de 2026-10-20:** versões inglesa e portuguesa revisadas, quatro páginas cada; seis autores USP e contato correspondente confirmados; sem financiamento. [Relatório técnico](submission/technical-review-20261020.md), [campos para EDAS](submission/edas-draft.md) e [auditoria pública](artifact/README.md). Não cadastrar nem enviar ao ICCE/EDAS sem nova instrução do usuário.

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
