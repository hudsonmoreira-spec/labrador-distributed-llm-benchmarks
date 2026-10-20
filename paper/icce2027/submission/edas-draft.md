# EDAS preparation draft

Prepared 2026-10-20. Technical fields and requester-supplied contacts are prepared; the requester states that all coauthors agree. Some metadata remains pending. No EDAS action has been performed.

## Title

An Experimental Study of RPC Inference on Resource-Constrained ARM Single-Board Computers

## Abstract

Partitioning a language model across inexpensive edge devices can extend available memory, but its latency cost must be measured on the target platform. This paper evaluates the RPC backend of llama.cpp on Caninos Labrador ARM single-board computers with approximately 1.9 GiB of OS-visible memory each. We compare five selected valid executions per condition: notebook-only, an isolated Labrador, and a notebook coordinating two Labrador RPC workers. Qwen2.5-1.5B-Instruct Q5_K_M is evaluated with a fixed prompt, 32 generated tokens, greedy sampling, and a fixed runtime revision. Paired worker logs establish layer assignment and graph execution on both workers. Mean process time increases from 43.86 s on the isolated board to 168.67 s with two RPC workers, taking 3.85 times as long. Prompt-processing and generation times are 1.95 and 1.91 times the isolated-board values, respectively; the larger process-time penalty therefore also involves time outside those measured phases. That remainder is not independently attributable to loading or communication. The contribution is an auditable case study of distributed execution without latency improvement in the tested configuration. The findings inform deployment evaluation for local consumer AI while remaining limited to one model, one short workload, and the selected executions.

## Keywords

edge AI; consumer electronics; ARM SBC; local inference; RPC; reproducibility

## Recommended track

IOT — Internet of Things (IoT) & Edge Computing with Edge AI.

Rationale: the paper evaluates local model-distributed inference on constrained ARM edge devices, with evidence of remote worker participation and a comparison of process/phase timings. It is an experimental deployment study rather than a new learning method. The exact available EDAS track label should be checked when registering; the conference homepage and call-for-papers page use different wording for IOT.

Alternative if preferred by the authors: MDA — Advanced AI and Agentic AI for Affordable and Low Power Consumer Electronics. No energy or agentic behavior is measured, so these should not be claimed in the submission summary.

## Contribution statement for author review

An auditable platform case study distinguishes successful RPC worker participation from a latency advantage. Five selected valid executions per condition compare notebook-only, isolated ARM, and notebook-plus-two-worker configurations. Preserved logs support per-worker layer/graph evidence and separate process time, runtime phase timings, and an unattributed arithmetic remainder. The results characterize this configuration and workload without claiming general cluster scalability.

## Artifact URL

https://github.com/hudsonmoreira-spec/labrador-distributed-llm-benchmarks/tree/7d94be29fe4e8069f2c916cb8cd0350acf338f1e

This is the evidence snapshot cited in the paper. Use an immutable author-approved manuscript revision when identifying the final PDF. Do not replace the evidence citation with a moving branch link.

## Coauthor contacts supplied by the requester

- Hudson Moreira Guimarães dos Santos — USP — hudson.moreira@usp.br — corresponding author.
- Bruno Cavalcante de Souza Sanches — USP — bruno.csanches@usp.br
- Laisa Caroline Costa De Biase — USP — laisa.costa@usp.br
- Roseli de Deus Lopes — USP — roseli.lopes@usp.br
- Marcelo Knörich Zuffo — USP — mkzuffo@usp.br
- Pablo Cesar Calcina Ccori — USP — email pending.

Hudson's name/email and corresponding-author role are confirmed. All coauthors' agreement is accepted as stated by the requester; no extra consent document is required.

## Funding

None, as confirmed by the requester. The manuscript states: “This research received no external funding.” No grant, donation, or sponsorship is inferred from use of the Labrador boards.

## Submission authorization and access

The requester authorizes publishing the latest revision on GitHub, but subsequently instructed that nothing is to be registered or submitted to ICCE/EDAS yet. This draft is preparation only. No EDAS registration or upload has been performed. Pablo's email is still pending.

## Fields requiring author decisions

Complete Pablo's email; any EDAS-required identifiers; conflicts; originality and simultaneous-submission declarations; final track and keywords; presenter and registration arrangements. Do not automatically confirm any declaration on behalf of an author.

## Official process checked on 2026-10-20

- Initial submission: PDF through https://edas.info/N35272 using the IEEE conference template on US Letter, no biographies, within the announced up-to-six-page limit.
- Paper deadline: 2026-10-31, final extension. The public page does not establish an exact timezone/cutoff; check EDAS before relying on a last-day upload.
- Acceptance notification: 2026-11-20; camera-ready: 2026-11-30.
- PDF eXpress is not required initially; it is required for the accepted final PDF. Conference ID remains TBA on the guidelines page. Copyright is handled through EDAS at the final stage.
- The event is in person, 2027-01-08 to 2027-01-11, Las Vegas. Publication requires Full registration as stated in the call for papers.

Sources: [submission guidelines](https://icce.org/2027/submission-guidelines/), [calendar](https://icce.org/2027/), [tracks and registration](https://icce.org/2027/call-for-papers-2/).
