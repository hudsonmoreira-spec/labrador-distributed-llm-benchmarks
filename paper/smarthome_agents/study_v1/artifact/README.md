# Evidências públicas — artigo de smart home

Este artefato pertence a **Simulated Smart-Home Control with Small Language Models on SBCs: Task Success, Latency, and Replication**. O estudo RPC de `paper/icce2027/` é separado e não fornece os resultados deste artigo.

## Snapshot e acesso

Snapshot imutável citado no PDF: [a834b8255f736fb59425b146be183c17866a2c7d](https://github.com/hudsonmoreira-spec/labrador-distributed-llm-benchmarks/tree/a834b8255f736fb59425b146be183c17866a2c7d).

O arquivo desse commit foi baixado do GitHub **sem autenticação** e verificado em 2026-10-20. A auditoria passou: 3.021 arquivos por SHA-256, 18 arquivos congelados intactos, 27 arquivos de análise reconstruídos byte a byte e 19 fontes de tabelas/figuras e resumos reconstruídas byte a byte. Não houve acesso às placas ou nova inferência.

Relatório: [public-evidence-audit-20261020.json](public-evidence-audit-20261020.json). Manifesto: [evidence-manifest.json](evidence-manifest.json). O manifesto cobre os insumos e resultados do estudo, não todos os arquivos históricos do repositório.

## Verificação com a revisão atual

```bash
git clone --branch smarthome-multiagent https://github.com/hudsonmoreira-spec/labrador-distributed-llm-benchmarks.git
cd labrador-distributed-llm-benchmarks
python3 experiments/smarthome_agents/scripts/verify_submission_artifact.py --output /tmp/smarthome-audit.json
```

O verificador e a opção de proveniência determinística do gerador são adicionados nesta revisão; não estavam no snapshot antigo. A revisão atual verifica os arquivos científicos contra os hashes do snapshot imutável. Não usa os modelos locais não rastreados.

Para verificar um arquivo extraído do commit citado, execute o verificador a partir da revisão atual com `--source /caminho/do/snapshot`. A reconstrução ocorre em diretório temporário e não sobrescreve os dados-fonte. Python 3 e sua biblioteca padrão bastam; os gráficos/PDFs só exigem LaTeX na etapa de compilação.

## Mapa

| Material | Caminho na raiz do repositório |
|---|---|
| Protocolo, configuração, cenários, identidade dos modelos | `experiments/smarthome_agents/study_v1/` |
| Respostas, requisições, estados e resultados de qualidade | `experiments/smarthome_agents/runs/20261006-study-v1-quality/` |
| Quatro julgamentos assistidos preservados | `experiments/smarthome_agents/runs/20261006-study-v1-quality/manual_reviews.json` |
| Respostas e 18 lotes de replicação | `experiments/smarthome_agents/runs/20261006-study-v1-scale/` |
| Hashes, propriedades e processos das seis placas | `experiments/smarthome_agents/runs/20261006-study-v1-final-audit/` |
| Análises publicadas para comparação | `experiments/smarthome_agents/analysis/quality-v1/` e `scale-v1/` |
| Avaliador e scripts congelados | `experiments/smarthome_agents/scripts/study_v1.py`, `analyze_study_v1.py` e manifesto `freeze.json` |
| Contagem separada de comandos | `experiments/smarthome_agents/scripts/analyze_action_steps_v1.py` |
| Gerador de tabelas e fontes das figuras | `experiments/smarthome_agents/scripts/make_study_assets.py` |
| Auditoria desta revisão | `experiments/smarthome_agents/scripts/verify_submission_artifact.py` |

## O que é verificado

- 240/240 tentativas de qualidade e 108/108 de replicação; duas campanhas anteriores de 48 tentativas preservadas.
- Reconstrução a partir de respostas brutas, com conferência do estado, permissões e avaliação registrados.
- 40 cenários em cinco categorias de oito casos, duas repetições por condição.
- Parâmetros de requisição, início após congelamento e ausência de sobreposição de inferências por placa nos registros do controlador.
- Janela de cada lote recalculada do primeiro despacho à última resposta; contagens, taxas e número de placas conferidos.
- Mesmos modelos, runtime/bibliotecas e parâmetros nos registros das seis placas; RAM visível de aproximadamente 1,89 GiB.
- Taxas de sucesso automáticas de 42/80, 30/80 e 12/80. Nenhum sucesso vem da revisão assistida.

## Limites

Quatro classificações assistidas de esclarecimento aguardam validação humana nos registros originais. Tratá-las provisoriamente como insucesso preserva os números automáticos; aceitar as quatro elevaria o 0.5B de 37,5% para 42,5%, ainda abaixo das regras (52,5%). Isso é um limite de sensibilidade, não revisão humana.

A casa e as ações são simuladas. A replicação é de servidores independentes, não divisão de um modelo ou colaboração de agentes. A taxa em lotes instrumentados não estabelece capacidade máxima, saturação ou tempo até atuação física. Os modelos e o runtime não são distribuídos neste pacote: há identificação por hash e registros de configuração. As fontes oficiais dos modelos são verificadas em [model-reference-verification-20261020.json](model-reference-verification-20261020.json).

O artefato mantém identificadores originais já públicos. Esta verificação não realiza auditoria completa de segredos/licenças de todo o histórico e não escolhe uma licença de redistribuição para os autores. Não altera protocolo, prompts, avaliador, respostas, ledger ou resultados publicados.
