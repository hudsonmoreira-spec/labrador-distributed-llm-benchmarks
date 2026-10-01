# Preliminary testbed selection

Basis: run `data/runs/20261001T150951Z`. The selection uses only inventory and lightweight diagnostics; it is not an LLM benchmark result.

## Primary nodes (16)

`node01` (192.168.50.42), `node02` (192.168.50.118), `node03` (192.168.50.231), `node04` (192.168.50.74), `node05` (192.168.50.44), `node06` (192.168.50.75), `node07` (192.168.50.71), `node08` (192.168.50.241), `node14` (192.168.50.140), `node22` (192.168.50.142), `node11` (192.168.50.143), `node13` (192.168.50.144), `node21` (192.168.50.175), `node23` (192.168.50.245), `node20` (192.168.50.247), `node19` (192.168.50.141).

Criterion: same model/architecture/CPU count and approximately 2 GiB across accessible nodes; nodes with approximately 1.2–1.8 GiB available in the sample were prioritized, without automatically replacing load observations. `node08` and `node17` were retained to complete a representative testbed, but showed high observed load and must be rechecked immediately before the pilot.

## Reserve nodes (8)

- `node10`/192.168.50.129: approximately 60 MiB of observed available RAM.
- `node09`/192.168.50.169: approximately 319 MiB of observed available RAM.
- `node12`/192.168.50.195 and `node15`/192.168.50.54: approximately 60 MiB available, with high load.
- `node16`/192.168.50.85, `node18`/192.168.50.240, and `node24`/192.168.50.89: approximately 60 MiB available; tools and load must be rechecked.
- `node17`/192.168.50.200: comparable hardware, but high observed load (approximately 2.4).
- `node19`/192.168.50.141: access now confirmed and high available RAM; retain as a primary node with swap-enabled caveat.

## Common issues

All accessible nodes reported a `machine-id` beginning with `11b02da9`, and repeated hostnames were observed (`labrador`, `lab1`–`lab8`). This is evidence of cloned system identity, not proof of duplicate MAC addresses: observed Ethernet MACs differ. Do not correct automatically; confirm with the image owner and use verified IP/MAC pairs as operational identity.

`iperf3`, compilers, Git, and LLM runtimes vary by board. A missing runtime was not interpreted as a defect. No pairwise TCP throughput test was performed because it would require starting a server/service or a coordinated session, which was not authorized at this stage.
