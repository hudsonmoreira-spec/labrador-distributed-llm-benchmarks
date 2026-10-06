# Acompanhamento do manuscrito atualizado

A prévia inicial está preservada em `../preview_20261005/`. O primeiro artigo permanece em `paper/icce2027/`, sem alterações por este estudo. Este diretório contém fontes e PDFs revisados das versões em inglês e português, produzidos com as campanhas completas.

Autoria e ordem propostas para apreciação: Hudson Moreira; Marcelo Knörich Zuffo; Laisa Costa de Biase. Não representam aceite dos orientadores. Afiliações, departamentos oficiais, e-mails e identificadores continuam pendentes conforme `../preview_20261005/review.md`; nenhum dado foi inventado.

Escopo final: regras, Qwen2.5-0.5B/1.5B Q5_K_M, réplicas independentes em 1/3/6 Labradores, casa inteiramente simulada. Colaboração e cache comparativo são trabalho futuro. Não houve envio a pessoas, submissão ou merge em main.

Protocolo congelado no commit `2bab455`; código de referência `72beda0`; manifesto em `experiments/smarthome_agents/study_v1/freeze.json`. Todas as tentativas ficam preservadas e números são reconstruídos dos arquivos individuais, com revisão caso a caso anexada quando necessária.

## Pontos para os orientadores

- Autoria/ordem, afiliações e contatos finais; venue e requisitos editoriais.
- Cobertura limitada dos casos e da gramática de regras. Os 40 casos são pedidos/estados elaborados, não casas independentes; a construção não testa pedidos idempotentes e favorece uma estratégia de inverter o estado em rotinas com as duas luzes. Não generalizar precisão.
- Comparação de configurações completas, com dois servidores residentes por placa e registros de serviços anteriores. Não atribuir diferenças exclusivamente ao número de parâmetros.
- Julgamentos semânticos assistidos por Codex devem ser apreciados pelos autores; eles não são apresentados como revisão humana. Contagens automáticas e após revisão são separadas.
- Taxa de lotes instrumentados não é capacidade máxima. Regras podem ter a taxa dominada pela instrumentação, apesar de latência HTTP curta.
- Financiamento, agradecimentos, conflitos, divulgação do uso de IA e aprovação final do texto antes de eventual submissão.

A identidade dos arquivos de modelo foi conferida em 2026-10-06 por hashes iguais aos publicados nos GGUF oficiais da Qwen. A nota da prévia permanece como registro do que se conhecia em 2026-10-05.

A taxa de tarefas corretas usa a janela HTTP já definida no protocolo: primeiro despacho até última resposta, com a decisão julgada depois pelo simulador. Não mede tempo até a aplicação final da mudança de estado. Essa distinção deve acompanhar a interpretação de escala e não ser apresentada como capacidade máxima ou taxa operacional de uma casa real.

## Conferência final do artefato

Em 2026-10-06: qualidade240/240, escala108/108 (18 lotes), duas campanhas de desenvolvimento48/48 cada. Todos os 18 arquivos congelados mantiveram SHA-256; auditoria final confirmou modelos e runtime/bibliotecas nas seis placas. Dados de qualidade commit938184b; escala/auditoria commitd2efabd.

PDFs IEEE de conferência, US Letter, quatro páginas cada. Todas as páginas foram renderizadas e inspecionadas: títulos/autoria, tabelas com unidades e n, figuras, margens, referências e quebras. A última página tem colunas equilibradas; compilação final sem referências indefinidas ou caixas excedendo margens. Tabelas/figuras derivadas pelos scripts do README, sem números simulados de hardware ou inferência.

- `main_en.pdf`: SHA-256 `53b7f7e5ad3bf4c10624aa29dc1c10ca7a5bb6d7c13178a497edb455ecf704ae`.
- `main_pt.pdf`: SHA-256 `e77dde36dea4ca1f7b1bbdc8f538955b0e8fe46468f07f1b7971e68d199bfc37`.
