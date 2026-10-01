# Labrador Distributed LLM Benchmarks

Repositório de materiais experimentais para o estudo de inferência distribuída de modelos de linguagem em uma bancada Labrador.

## Estado atual

O material incorporado em [`research/`](research/) corresponde à etapa de caracterização da bancada: inventário, diagnósticos leves, seleção preliminar de nós e planejamento do piloto. Ele ainda **não contém resultados de benchmark de inferência**.

Os resultados devem ser interpretados com base em três propriedades: rastreabilidade da execução, separação entre observação e interpretação e possibilidade de reprodução. Por isso, cada execução mantém seus dados brutos, horário UTC e scripts usados para gerar os relatórios.

## Organização

- [`research/data/runs/`](research/data/runs/) — evidências brutas por execução e por nó;
- [`research/data/`](research/data/) — inventários derivados em CSV e JSON;
- [`research/reports/`](research/reports/) — relatórios, seleção preliminar e plano de contingência;
- [`research/scripts/`](research/scripts/) — coleta e geração dos relatórios;
- [`docs/ieee/`](docs/ieee/) — guia de organização, reprodutibilidade e publicação do material suplementar.

## Reprodução

```bash
cd research
./scripts/discover.sh
./scripts/diagnostics.sh
python3 scripts/build_reports.py
```

Os scripts de descoberta usam somente comandos de leitura e `sudo -n`; não executam inferência, não instalam pacotes, não iniciam serviços e não reiniciam os nós.

## Aviso de publicação

Os artefatos foram preservados para auditoria, mas contêm endereços de uma rede privada, nomes de host, identificadores de máquina e chaves SSH conhecidas. Antes de tornar o repositório público ou anexá-lo a um artigo, aplique a sanitização descrita em [`docs/ieee/publication-checklist.md`](docs/ieee/publication-checklist.md).
