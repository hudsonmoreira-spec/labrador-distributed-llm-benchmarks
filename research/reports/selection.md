# Seleção preliminar da bancada

Base: execução `data/runs/20261001T150951Z`. A seleção usa apenas inventário e diagnósticos leves; não é resultado de benchmark de LLM.

## Principais (16)

`node01` (192.168.50.42), `node02` (192.168.50.118), `node03` (192.168.50.231), `node04` (192.168.50.74), `node05` (192.168.50.44), `node06` (192.168.50.75), `node07` (192.168.50.71), `node08` (192.168.50.241), `node14` (192.168.50.140), `node22` (192.168.50.142), `node11` (192.168.50.143), `node13` (192.168.50.144), `node21` (192.168.50.175), `node23` (192.168.50.245), `node20` (192.168.50.247), `node19` (192.168.50.141).

Critério: mesmo modelo/arquitetura/número de CPUs e aproximadamente 2 GiB em todas as acessíveis; priorização dos nós com cerca de 1,2–1,8 GiB disponíveis na amostra, sem substituir automaticamente a observação de carga. `node08` e `node17` foram mantidos para completar uma bancada representativa, mas têm carga observada elevada e devem ser rechecados imediatamente antes do piloto.

## Reservas (8)

- `node10`/192.168.50.129: RAM disponível observada ~60 MiB.
- `node09`/192.168.50.169: RAM disponível observada ~319 MiB.
- `node12`/192.168.50.195 e `node15`/192.168.50.54: ~60 MiB disponíveis e carga elevada.
- `node16`/192.168.50.85, `node18`/192.168.50.240 e `node24`/192.168.50.89: ~60 MiB disponíveis; ferramentas/carga devem ser rechecadas.
- `node17`/192.168.50.200: hardware comparável, mas carga observada elevada (~2,4).
- `node19`/192.168.50.141: acesso agora confirmado e RAM disponível alta; manter como principal com ressalva de swap habilitado.

## Problemas comuns

Todos os nós acessíveis reportaram machine-id iniciado por `11b02da9` e houve nomes de host repetidos (`labrador`, `lab1`–`lab8`). Isso é evidência de identidade clonada no sistema, não prova de MAC duplicado: os MACs Ethernet observados diferem. Não corrigir automaticamente; confirmar com o responsável pela imagem e usar IP/MAC verificados como identidade operacional.

`iperf3`, compiladores, Git e runtimes de LLM variam por placa. A ausência de runtime não foi interpretada como defeito. Não houve teste de vazão TCP entre pares porque isso requer iniciar servidor/serviço ou uma sessão coordenada, ainda não autorizada.
