# Public evidence for the ICCE RPC paper

Use the existing **Labrador Distributed LLM Benchmarks** repository. The RPC study and smart-home study have separate paper and data directories; a second repository is not needed to reproduce this paper.

## Frozen evidence already published

Repository: https://github.com/hudsonmoreira-spec/labrador-distributed-llm-benchmarks

Evidence snapshot: https://github.com/hudsonmoreira-spec/labrador-distributed-llm-benchmarks/tree/7d94be29fe4e8069f2c916cb8cd0350acf338f1e

This is the immutable evidence commit cited by the manuscript, not the latest manuscript revision. The refreshed LaTeX/PDF and this audit are distributed together in the manuscript update on branch `smarthome-multiagent`. Keep the evidence citation pinned even when publishing a newer manuscript.

A reviewer can reconstruct the three published CSVs with Git and Python 3 (standard library only):

```bash
git clone https://github.com/hudsonmoreira-spec/labrador-distributed-llm-benchmarks.git
cd labrador-distributed-llm-benchmarks
git checkout --detach 7d94be29fe4e8069f2c916cb8cd0350acf338f1e
python3 research/scripts/analyze_rpc_validation.py
git diff --exit-code -- research/data/derived/rpc-validation-20261004.csv research/data/derived/rpc-validation-20261004-summary.csv research/data/derived/rpc-validation-20261004-failures.csv
```

An empty diff means the reconstructed CSVs match the published files exactly. These commands do not connect to the boards, start a service, download a model, or run inference.

## Artifact map

| Evidence | Location |
|---|---|
| Client logs, statuses, worker traces, manifests | `research/data/runs/*/rpc-validation/` |
| All 55 attempts and selection flags | `research/data/derived/rpc-validation-20261004.csv` |
| Selected-condition statistics | `research/data/derived/rpc-validation-20261004-summary.csv` |
| Excluded failure inventory | `research/data/derived/rpc-validation-20261004-failures.csv` |
| Offline reconstruction | `research/scripts/analyze_rpc_validation.py` |
| Hardware/runtime/model hashes and build details | `paper/icce2027/artifact/build-recipe.md` |
| Local runtime patch | `paper/icce2027/artifact/llama.cpp-local.patch` |
| ARM compilation and packaging recipes | `ops/cross_compile_llama.sh`, `ops/package_cross_llama.sh` |

## Extended verification added with this audit

From a checkout containing the new verifier and manifest:

```bash
python3 research/scripts/verify_icce_artifact.py
```

To verify a separate extracted public snapshot without changing it:

```bash
python3 research/scripts/verify_icce_artifact.py --source /path/to/extracted-snapshot --output /tmp/icce-audit.json
```

The verifier checks SHA-256 for 507 evidence files, reconstructs the CSVs in a temporary directory, compares all three byte for byte, checks the 55-attempt inventory and five selected valid executions per condition, and checks graph/tensor activity for both workers in each selected RPC request. It also checks the reported mean process times and the 32 excluded failures. Any failed check returns a nonzero exit status.

The manifest is anchored to the published evidence commit. It excludes unrelated local/untracked experiments. It does not assert that all historical files in the repository have been audited.

## Scope and remaining publication tasks

This verifies reconstruction from preserved logs. It does not independently rerun hardware experiments, measure network throughput, establish peak memory use, or certify every interpretation in the manuscript. The build recipe records hashes; the model and compiled runtime packages are not claimed to be distributed in this artifact.

The repository is public and retains original testbed identifiers. This audit does not change that publication policy or perform a comprehensive secret/license audit. No top-level reuse license was found; authors should choose appropriate terms before encouraging redistribution. Public access alone does not grant a reuse license.

The updated manuscript, verifier, manifest, and report accompany this revision on `smarthome-multiagent`. Before submission, confirm that the branch contains the intended author-approved version. A tag/release can identify the submission version in this same repository; a DOI archive is optional. Do not replace the frozen evidence citation with a moving branch URL.
