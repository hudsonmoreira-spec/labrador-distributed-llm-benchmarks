# Inventário do cluster Labrador

Este repositório contém a descoberta de leitura e os diagnósticos leves da bancada Labrador. A descoberta não executa inferência, não instala pacotes, não inicia serviços, não reinicia placas e não realiza testes destrutivos.

## Repetição

```bash
./scripts/discover.sh
./scripts/diagnostics.sh
python3 scripts/build_reports.py
```

Os hosts estão em `config/hosts.txt`. Os dados brutos ficam em `data/runs/<UTC>/hosts/` e `data/runs/<UTC>/controller/`; cada host tem `metadata.json`, `raw.txt` e `error.txt`. O arquivo `known_hosts` usado pela coleta fica em `data/ssh/` e não contém chaves privadas.

Por padrão são usados `caninos`, `ConnectTimeout=6`, `ServerAliveInterval=5`, `ServerAliveCountMax=1`, modo não interativo e até quatro conexões simultâneas. A descoberta remota usa somente comandos de leitura e `sudo -n`; uma falha não bloqueia os demais hosts.

Os diagnósticos curtos devem ser executados após a descoberta e não substituem benchmarks longos. O relatório final e a seleção ficam em `reports/`.
