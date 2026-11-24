# Placas de reserva dos testes — 23/11/2026

As reservas usam Ethernet. O endereço DHCP pode mudar; conferir o MAC e a identidade do ambiente antes de reutilizá-las. Não identificar uma placa somente pelo hostname ou machine-id, pois há imagens clonadas na rede.

| Reserva | IP Ethernet atual | RAM | Runtime | Uso |
|---|---|---|---|---|
| lab4 | 192.168.50.85 | aproximadamente 1,89 GiB | b9584-e25a32e98 | Substituição de um worker |
| lab6 | 192.168.50.200 | aproximadamente 1,89 GiB | b9584-e25a32e98 | Substituição de um worker |

A versão do runtime, o executável, as bibliotecas compartilhadas e o modelo de 1,5B conferem com o ambiente recuperado. A validação em `backup_validation/` carregou o modelo e gerou um token em cada reserva; esse teste não mede acurácia. As reservas não contam como placas do experimento original e não geram um novo resultado de escala de seis réplicas.

Os arquivos de preparação ficam em `/home/caninos/smarthome_agents/revision_20261123_backup/` nas placas. Os launchers `start-1.5b.sh` e `start-0.5b.sh` foram instalados. Ambos os modelos foram carregados e geraram um token de verificação em cada reserva; os hashes dos arquivos conferem com os modelos originais. Cada launcher usa CPU, quatro threads, contexto 512, uma requisição por vez e porta 19115. Os serviços anteriores e a configuração de rede não foram alterados. O servidor temporário da validação foi encerrado; a reserva pode ser iniciada pelo coordenador quando necessária.

## Política de substituição

1. Preservar a requisição original, resposta, horário e erro de transporte/infraestrutura, quando existente.
2. Não repetir uma resposta concluída apenas porque ela foi incorreta ou porque uma coleta de memória posterior falhou.
3. Registrar o worker originalmente previsto, a reserva utilizada e o motivo da troca antes de despachar os casos ainda não executados.
4. Usar exatamente o mesmo arquivo de modelo, prompt, esquema JSON, seed e parâmetros do protocolo aplicável. Nenhum dado do avaliador é enviado ao modelo.
5. Manter uma inferência ativa por placa. Separar falha de rede de erro de interpretação do modelo.
6. Divulgar a substituição e a limitação de comparabilidade temporal. Não misturar a campanha complementar com os 240 resultados reservados originais.
7. Encerrar somente o processo temporário identificado pela porta e pelo arquivo de PID da campanha; preservar os serviços existentes.

O inventário `backup_pool.json` registra as reservas validadas. A disponibilidade de uma reserva deve ser conferida novamente no momento da troca; a preparação não elimina falhas de energia, switch ou rede.
