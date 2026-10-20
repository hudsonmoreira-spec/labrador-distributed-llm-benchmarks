# Technical and bibliographic review — 2026-10-20

## Result

The technical preparation is complete for author review. This is an experimental case study of selected valid executions, not a causal isolation of network cost, a reliability sample, or a general scaling result. No new hardware experiments, author approval, EDAS registration, or conference submission were performed.

## Corrections made

- Replaced “controlled comparison” with “experimental comparison”. Campaign and build differences remain explicit.
- Corrected 1.99 GiB RAM to 1.89 GiB OS-visible RAM. Preserved records for both RPC workers report `MemTotal: 1986400 kB`: 1,986,400 KiB / 1,048,576 = 1.894378662 GiB. Abstract and broader descriptions now use approximately 1.9 GiB.
- Corrected EdgeShard coauthor **Song Jiang → Shan Jiang**, using publisher-deposited metadata and the PolyU institutional record.
- Clarified that matching x86-client hashes in manifests do not establish identical x86/ARM executables.
- Described temperature-zero generation as greedy sampling rather than implying reproducibility independent of builds/hardware.
- Limited the deployment conclusion to the selected workload/configurations; low SD describes selected-case dispersion rather than broad repeatability.
- Corrected the patch description to `common` and the vendor HTTP library. The patch does not establish that all inference kernels were compiled at `-O0`.
- Distinguished Python-only offline reconstruction from the historical runtime build record, which depends on an external source checkout, a Debian sysroot, and other prerequisites.
- Replaced hard-coded table/figure/equation numbers with LaTeX references.
- Expanded the AI disclosure to include the reconstructed diagram/plot and this technical/bibliographic review.
- Replaced stale two-author checklists with a pending-decision checklist for the six names already supplied; no author metadata was invented.
- Updated the local ICCE deadline checklist from October 15 to October 31, 2026.

## Claims checked against preserved evidence

Run from the repository root:

```bash
python3 research/scripts/audit_icce_claims.py --output /tmp/icce-claims.json
```

This first performs the frozen-evidence hash and byte-for-byte CSV verification, then checks raw client logs, worker traces, selected-campaign manifests, and dated hardware records. The recorded result is [claims-audit-20261020.json](../artifact/claims-audit-20261020.json); every additionally examined raw input has a SHA-256 entry there.

| Claim | Evidence/check | Result |
|---|---|---|
| 55 attempts, 15 selected valid cases | Published per-case CSV reconstructed from raw logs | Pass; 23 total valid cases, eight outside selection, 32 failures |
| Five selected cases per condition | Explicit run/case selection | Pass; 5 notebook, 5 ARM, 2+3 RPC across two campaigns |
| Model/source/recorded x86 client/patch identity | Four selected-campaign manifests | Matching recorded hashes; ARM executable remains a distinct build |
| Workload parameters | Manifest context, threads, offload argument, output limit, temperature, seed, EOS and warmup flags | Pass; 38 prompt tokens, 32 generated tokens in every selected execution |
| Normal completion and client thread count | Raw client logs | Pass; exit zero and four client threads; worker thread count remains unknown |
| 28 transformer blocks and remote assignment | Each selected RPC client log | Pass; logical layers 0–14 on RPC0, 15–28 on RPC1 |
| Both workers execute graph/tensor operations | Each selected RPC paired server trace | Pass in all five requests; no utilization percentage inferred |
| Representative event counts | `matrix-validation-7/rep-3-rpc-2.server.log` | Per host: 3 compute, 30 recompute, 33 get; set counts 345 and 356 |
| Table I | Selected process times and sample SD/min/max | Pass: means 5.69, 43.86, 168.67 s |
| Table II and stacked plot | Per-execution phase conversion/remainder; mean of runtime rate fields | Pass; remainders 2.042, 8.536, 100.682 s; rates 12.78, 1.60, 0.84 tok/s |
| RPC/ARM ratios | Unrounded means | 3.84569 process; 1.94866 prompt; 1.90504 generation |
| Residual shares | Mean residual / mean process time | ARM 19.461%; RPC 59.691%; not a measured network/loading phase |
| Table III | Reconstructed failure-class counts | Pass; 16 connection/startup, 10 preparation/tool/host, 1 loading, 3 incomplete, 2 partial |
| Board CPU/OS/RAM/swap/link evidence | Frozen October 1 inventory for worker hosts `.42` and `.118` | Cortex-A53, four cores, Debian 12, kernel 6.1.76, 1.894 GiB, zero swap; dated 100 Mbps/full-duplex link messages |

Hardware records predate the inference campaign. They establish the recorded configuration and link negotiation, not experiment-time throughput, thermal behavior, exclusive resource use, or peak memory.

## Bibliographic review

All seven entries have a source and a defined role. Publisher-deposited Crossref metadata for the three research publications is recorded in [bibliographic-metadata-20261020.json](../artifact/bibliographic-metadata-20261020.json). The IEEE Xplore renderer returned a bot challenge; authors' papers and institutional records supplied the content check instead. No unsupported claim is inferred from that inaccessible renderer.

| Entry | Verification and supported use |
|---|---|
| Jang and Morabito, Edge-First | [EURECOM record](https://www.eurecom.fr/publication/8442), [authors' paper](https://arxiv.org/html/2505.16508v1), publisher-deposited [DOI metadata](https://api.crossref.org/works/10.1109%2FICDCSW63273.2025.00058). Authors, ICDCSW 2025, pp. 309–314 and DOI match. The paper supports separate quality, TTFT, generation, energy and cost evaluation; no numerical result is transferred to Labrador. |
| Qwen2.5 report | [Version v2](https://arxiv.org/abs/2412.15115v2): revised January 3, 2025. Supports model-family and quantized-variant context, not independent identification of the exact experimental GGUF; its identity is recorded by hash in the artifact. |
| MDI-LLM | [Authors' paper](https://arxiv.org/html/2505.18164v1), [author publication list](https://erdemkoyuncu.github.io/publications.html), publisher-deposited [DOI metadata](https://api.crossref.org/works/10.1109%2FLANMAN66415.2025.11154542). Authors, LANMAN 2025, pp. 1–6 and DOI match. Supports partitioning, multi-sequence recurrent pipelining and memory-capacity motivation. |
| EdgeShard | [PolyU record](https://research.polyu.edu.hk/en/publications/edgeshard-efficient-llm-inference-via-collaborative-edge-computin/), [authors' preprint](https://arxiv.org/html/2405.14371v1), publisher-deposited [DOI metadata](https://api.crossref.org/works/10.1109%2FJIOT.2024.3524255). Final journal authors/order, vol. 12(10), pp. 13119–13131 and DOI match after correcting Shan Jiang. Supports adaptive joint device selection/partitioning; no cross-platform speed claim is made here. |
| llama.cpp RPC | Official source README at frozen commit `68e79bd8cd6b7995f8fce8da252b249bbf237e63`, inspected through `git show` in the local upstream checkout. Supports exposing remote devices and computation offloading. The [immutable source link](https://github.com/ggml-org/llama.cpp/tree/68e79bd8cd6b7995f8fce8da252b249bbf237e63/tools/rpc) is retained. |
| Experimental evidence | Public commit `7d94be29fe4e8069f2c916cb8cd0350acf338f1e`; anonymous download, 507 hashes and three byte-identical CSV reconstructions passed in the preceding public-evidence audit. |
| IEEE AI guidance | [IEEE policy](https://open.ieee.org/author-guidelines-for-artificial-intelligence-ai-generated-text/) identifies acknowledgments, the AI system, affected content and extent of use. Disclosure names the system and its role in sections, scripts and reconstructed figures. The requester states that all coauthors agree. |

## Scientific limits retained

Five selected cases per condition do not establish availability or population-level variability. One model/prompt/output length limits external validity. Campaign/launcher changes and x86/ARM builds prevent isolating architecture or network causality. Worker threads and the notebook distribution at experiment time are not recovered. There is no measured TTFT, loading-only time, network-transfer-only cost, peak RAM, energy, semantic output quality, or concurrent service workload. The study does not test models exceeding one board's memory.

These limitations are disclosed; they are not silently repaired by assumptions or by generating new data. Additional experiments may strengthen a later study but are outside this technical revision.

## Final PDF checks

The rebuilt PDF has **four US Letter pages**, embedded Type 1 fonts, no Type 3 fonts, no undefined references and no overfull boxes. All four final pages were rendered and visually checked, including title/authors, both figures, three tables, equation and seven references. The EDAS abstract matches the LaTeX abstract exactly after removing markup (192 whitespace-delimited words). The supplied author order is unchanged. Following the requester's confirmation, Pablo shares the USP affiliation marker with the other five authors.

The PDF SHA-256 and machine-readable checks are in [pdf-check-20261020.json](pdf-check-20261020.json). PDF eXpress was not run; the ICCE initial-submission guidelines do not require it. These checks are not a PDF eXpress certificate.

## Submission preparation and author decisions

[edas-draft.md](edas-draft.md) contains the exact revised title, abstract, keywords, IOT-track rationale, artifact link and current official process. It is a preparation document, not an EDAS submission.

The requester confirms all coauthors' agreement and USP affiliation for all six authors. Hudson Moreira Guimarães dos Santos (hudson.moreira@usp.br) is the corresponding author, and the requester confirms no funding. Still complete Pablo's email and any actual EDAS-required declarations, final track, and presentation/registration arrangements. See [author-pending.md](../author-pending.md). A reuse license for the repository is an author decision; this review does not choose one.
