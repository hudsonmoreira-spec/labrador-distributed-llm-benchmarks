# ICCE 2027 candidate

The current candidate is a three-page IEEE Conference-format PDF, within the ICCE limit of up to six pages including references. It uses US Letter, two columns, no biographies, and the installed `IEEEtran` conference class.

Build from this directory:

```bash
../../research/scripts/analyze_rpc_validation.py
../../research/scripts/make_paper_assets.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The analysis script reconstructs the per-case CSV, selected-condition summary, and failure inventory from raw logs. It extracts the runtime's per-request `predicted_per_second` field; `derived_tokens_per_second` is retained separately as a ratio defined by this project. The asset script converts the summary into generated LaTeX macros. `main.pdf` was compiled and visually inspected as three letter-size pages. The plot is intentionally a compact mean comparison; the table carries sample standard deviation, minimum, maximum, and `n=5`.

Before submission, authors must confirm metadata, track, citations, funding/conflicts, AI-use disclosure, and the official deadline. Raw logs must be sanitized before public release because they contain private-network identifiers.
