# Pilot proposal (not executed)

## Objective

Compare a single request on one node and two nodes using the same artifact, quantization, prompt, and parameters. This qualifies as a distributed experiment only if the runtime partitions the same model across processes/nodes; two independent replicas are a different experiment.

## Open items

No distributed LLM runtime was confirmed in the inventory. Verify the version/commit, partitioning documentation, transport, model format, and instrumentation on each selected node and the controller. `llama.cpp`, Ollama, vLLM, MPI, and `iperf3` are absent from parts of the testbed; do not install or start anything at this stage.

## Planned commands

After installation/configuration approval, record `command -v`, `--version`, commit, and documentation; copy/verify the same model hash and use an explicit two-worker configuration. Run the control case on `node01` first, then the two-node case on `node01,node02`, using the same fixed prompt. The exact command depends on the selected runtime and must not be invented before verification.

## Required evidence

Store launcher and worker logs containing node/IP, rank, PID, loaded layers, model hash, UTC start/end, and request identifier. Confirm in the trace that both ranks participated in the same request. Without this evidence, classify the result as replication/routing, not model partitioning. Do not claim synchronization measurements without runtime instrumentation.
