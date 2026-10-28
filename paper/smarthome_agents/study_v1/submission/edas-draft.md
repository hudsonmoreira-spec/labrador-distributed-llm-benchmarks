# Preparação para o EDAS — artigo de smart home

**Somente preparação. Não cadastrar ou enviar ao ICCE/EDAS sem nova instrução do usuário.** Este documento é do estudo de casa inteligente simulada, não do artigo de RPC.

## Título

Simulated Smart-Home Control with Small Language Models on SBCs: Task Success, Latency, and Replication

## Resumo em inglês

We evaluate a finite-rule baseline and quantized Qwen2.5 models of 0.5B and 1.5B parameters on Labrador single-board computers (SBCs). The home and every action are simulated; hardware and inference are real. Forty reserved scenarios cover clear instructions, paraphrases, explicit routines, ambiguity, and invalid requests, with two repetitions per condition. Scenario-averaged success is computed from the two repetitions, while latency statistics describe individual requests. Mean scenario success was 52.5% for rules, 37.5% for 0.5B, and 15.0% for 1.5B, with request medians 0.157, 36.848, and 94.663 s, respectively. Independent replicas on one, three, and six boards serve a fixed six-request batch. The released attempts distinguish model proposals from executor interventions and preserve unsuccessful executions. The scope supports conclusions about the tested configurations and constructed cases, without claiming general residential accuracy or maximum service capacity.

## Palavras-chave

simulated smart home; small language models; SBC; evaluation; latency

## Trilha recomendada

**IOT — Internet of Things (IoT) & Edge Computing with Edge AI.**

Justificativa: controle doméstico simulado por linguagem natural em hardware ARM de borda, com avaliação conjunta de decisões, latência e replicação independente. Não reivindica atuação física, colaboração entre agentes ou medição de energia. A trilha MDA é alternativa; IOT é a recomendação pela aplicação doméstica e execução na borda. Confirmar o rótulo efetivamente disponível no EDAS.

## Autores e contatos

Ordem e concordância consideradas conforme informado pelo usuário; todos vinculados à University of São Paulo (USP), São Paulo, Brazil.

| Ordem | Autor | E-mail |
|---|---|---|
| 1 | Hudson Moreira Guimarães dos Santos — correspondente | hudson.moreira@usp.br |
| 2 | Bruno Cavalcante de Souza Sanches | bruno.csanches@usp.br |
| 3 | Laisa Caroline Costa De Biase | laisa.costa@usp.br |
| 4 | Roseli de Deus Lopes | roseli.lopes@usp.br |
| 5 | Marcelo Knörich Zuffo | mkzuffo@usp.br |
| 6 | Pablo Cesar Calcina Ccori | Pendente |

Não inventar e-mail para Pablo nem omiti-lo da autoria. Não é necessário pedir nova prova de concordância dos coautores.

## Financiamento e declarações

Sem financiamento, conforme confirmado pelo usuário. Redação no artigo: “This research received no external funding.” O uso das placas Labrador é descrito na metodologia; não foi inferido patrocínio, doação ou apoio institucional. Não foi inserido agradecimento opcional ao Caninos Loucos.

Uso de IA já descrito no PDF. Os quatro julgamentos semânticos assistidos permanecem identificados como pendentes de validação humana; nenhum sucesso depende deles. Concordância geral dos autores não foi usada para alterar esses registros históricos.

## Evidências

Snapshot citado no artigo:
https://github.com/hudsonmoreira-spec/labrador-distributed-llm-benchmarks/tree/a834b8255f736fb59425b146be183c17866a2c7d

O snapshot contém 240 tentativas de qualidade, 108 de replicação, o protocolo congelado e as análises. Não usar o commit `7d94be2` do estudo RPC como evidência deste artigo. Reconstrução pública e limites: [../artifact/README.md](../artifact/README.md).

## Processo oficial e pendências

- Portal: https://edas.info/N35272, indicado nas diretrizes do ICCE.
- Referência consultada nesta conversa em 2026-10-20: submissão inicial em PDF, template IEEE conference, US Letter, até seis páginas incluindo referências, sem biografias. O candidato inglês revisado em 28/10 tem cinco páginas; a versão histórica de 20/10 tinha quatro. A rota opcional de Transactions/periódicos associados exigiria condensação para quatro páginas.
- Prazo divulgado: 31/10/2026; aceite: 20/11/2026; camera-ready: 30/11/2026. Confirmar horário/fuso de encerramento no portal quando houver autorização para submeter.
- PDF eXpress não é exigido inicialmente; é exigido para a versão final aceita. Não foi executado.
- E-mail de Pablo ainda não informado. Eventuais identificadores e declarações adicionais dependem dos campos reais do EDAS; não criar obrigações hipotéticas.
- Inscrição/apresentador e quaisquer termos ou pagamentos ficam para decisão própria na etapa correspondente.

Fontes: [diretrizes](https://icce.org/2027/submission-guidelines/), [calendário](https://icce.org/2027/), [trilhas](https://icce.org/2027/call-for-papers-2/). As páginas de diretrizes/calendário apresentaram timeout na ferramenta web, mas foram recuperadas diretamente do site oficial e reconferidas em 2026-10-20. Conferir novamente o prazo e o fuso quando a submissão for autorizada. Nenhuma operação no EDAS foi realizada.
