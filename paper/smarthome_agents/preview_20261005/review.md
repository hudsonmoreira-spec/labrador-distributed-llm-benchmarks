# Prévia para apreciação dos orientadores — 2026-10-05

Título em português: Controle Doméstico Simulado com Modelos Pequenos em SBCs: Precisão, Latência e Escalabilidade.

Título proposto em inglês: Simulated Smart-Home Control with Small Language Models on SBCs: Accuracy, Latency, and Scalability.

Autoria e ordem propostas para apreciação: Hudson Moreira; Marcelo Knörich Zuffo; Laisa Costa de Biase. A lista não representa aceite de coautoria ou aprovação da ordem.

## Decisões para avaliação

- Confirmar autoria, ordem, títulos e adequação do escopo reduzido: regras, Qwen2.5 0.5B/1.5B e réplicas em 1/3/6 Labradores. Colaboração entre agentes fica como trabalho futuro.
- Confirmar as afiliações oficiais, contatos e identificadores de cada autor. O primeiro artigo registra informações de Hudson e Marcelo em `paper/icce2027/author-pending.md`, mas ainda contém pendências de aprovação. Não foi encontrada documentação verificada de afiliação de Laisa. Esta prévia omite blocos institucionais, e-mails e identificadores.
- Avaliar o conjunto reservado, os critérios de esclarecimento e a política geral de bloqueio antes da coleta principal, caso desejem propor mudanças de desenho. O desenvolvimento autorizado segue sem depender de aprovação editorial.
- Confirmar venue, limite de páginas, financiamento, agradecimentos e divulgação do uso de IA antes de submissão. Não houve submissão nem contato com orientadores.

## Evidência e limites

Referência do código e registros históricos: `3427be794fdb14df0689de594973f203551f7657`.

O script `analyze_pilot.py` lê os 12 `summary.json` individuais da campanha `20261005T1445-single-agent-chat-schema-1p5b-validatorfix`, verifica quatro casos com três repetições, 12 respostas estruturadas, nove tarefas concluídas e três bloqueios históricos. Os números não são uma estimativa de precisão geral. O executor histórico consultava `evaluator.prohibited_actions`; isso será corrigido sem reescrever os registros anteriores.

Reprodução a partir da raiz:

```bash
python3 paper/smarthome_agents/preview_20261005/analyze_pilot.py
cd paper/smarthome_agents/preview_20261005
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Esta pasta preserva a prévia inicial. Manuscritos atualizados devem usar outro caminho. O primeiro artigo permanece em `paper/icce2027/`.

## Revisão do PDF

`main.pdf`: duas páginas US Letter, IEEEtran conference. As duas páginas foram renderizadas com `pdftoppm` e inspecionadas visualmente: título/autoria legíveis, tabela dentro da coluna, referências completas e sem sobreposição ou corte nas quebras. Compilação final sem citações indefinidas ou caixas excedentes. A última página tem espaço livre, adequado à prévia de discussão; o balanceamento final será revisto no manuscrito completo.
