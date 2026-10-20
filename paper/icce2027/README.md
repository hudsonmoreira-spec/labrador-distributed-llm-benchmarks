# ICCE 2027 candidate

The current candidate is *An Experimental Study of RPC Inference on Resource-Constrained ARM Single-Board Computers*. On 2026-10-20, `main.tex` and `references.bib` were reconstructed from the PDF produced on another computer (`/home/hudymoreira/Downloads/main.pdf`, SHA-256 `604eb0fda8be61d48fd5e41e0f7b7a5eb2787adae4509f8506b9105d5cdaea31`). `main.pdf` is now compiled from these local sources, rather than copied from Downloads.

The text, authorship, numerical results, three tables, architecture diagram, phase-accounting equation, stacked timing plot, and seven references follow that reference PDF. The subsequent technical revision corrects memory units and bibliography, tightens claims against the preserved evidence, and clarifies reproduction limits. Figure geometry and page breaks may differ because the original source project was unavailable. The four-page output uses IEEEtran conference format, US Letter, two columns, and embedded fonts. All pages were rendered and visually checked; the final build has no undefined references or overfull boxes.

Public evidence, reviewer instructions, and audit scope: [artifact/README.md](artifact/README.md). The evidence commit remains `7d94be29fe4e8069f2c916cb8cd0350acf338f1e`; it is separate from the updated manuscript revision.

Technical revision and claims/reference checks: [submission/technical-review-20261020.md](submission/technical-review-20261020.md). Copy-ready EDAS fields: [submission/edas-draft.md](submission/edas-draft.md). Pending author decisions: [author-pending.md](author-pending.md).

Build from this directory:

```bash
python3 ../../research/scripts/make_paper_assets.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The asset script reads the preserved summary, failure inventory, and selected per-execution CSV under `research/data/derived/`. Phase remainders are computed for each selected valid execution as process seconds minus prompt seconds minus generation seconds, then averaged. No new inference or experiment is required to rebuild the paper.

To reconstruct the CSVs from preserved logs separately, run `python3 ../../research/scripts/analyze_rpc_validation.py` before generating assets. The runtime generation rate is the mean of each request's `predicted_per_second`, not the ratio of the token count to mean generation time.

Hudson Moreira Guimarães dos Santos (hudson.moreira@usp.br) is the corresponding author. The requester confirms no funding and authorizes GitHub publication. ICCE/EDAS registration and submission are on hold at the requester's explicit instruction. Complete Pablo's email and the actual EDAS-required declarations; confirm the official deadline. The requester states that all coauthors agree and confirms USP affiliation for all six authors. This source synchronization does not constitute author approval or conference submission. The smart-home paper is a separate study and remains unchanged.
