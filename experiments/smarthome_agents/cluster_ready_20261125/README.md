# Cluster parametrizado — 25/11/2026

Rede Ethernet 192.168.50.0/24. Identidades conferidas pelo MAC de end0, pois há nomes clonados. O host 192.168.50.141 foi excluído por solicitação explícita do usuário.

| Papel | Placa | IP atual |
|---|---|---|
| Principal | lab1 | 192.168.50.129 |
| Principal | lab2 | 192.168.50.89 |
| Principal | lab3 | 192.168.50.169 |
| Principal | lab7 | 192.168.50.240 |
| Principal | lab8 | 192.168.50.195 |
| Reserva | lab4 | 192.168.50.85 |
| Reserva | lab6 | 192.168.50.200 |

## Perfis comuns

Runtime b9584/e25a32e98, CPU, quatro threads de computação e lote, contexto512, um slot, limite de128 tokens, mesma quantização Q5_K_M. Os dois modelos, runtime e bibliotecas foram conferidos por SHA-256 nas sete placas. Modelos não foram duplicados: caminhos uniformes usam links para os arquivos originais verificados.

Porta isolada19115. Serviços systemd `smarthome-benchmark-05.service` e `smarthome-benchmark-15.service` são mutuamente exclusivos; `systemctl start` de um encerra o outro. O perfil0,5B é habilitado no boot; o1,5B fica disponível sob demanda. Ambos reiniciam automaticamente se o processo terminar inesperadamente. Não foi realizado novo reboot depois da instalação: habilitação de boot e recuperação do processo são verificadas separadamente. Nenhuma configuração de rede/Wi-Fi foi alterada e o serviço antigo8080 foi preservado.

Configuração remota: `/home/caninos/smarthome_agents/cluster_ready_20261125/profile.json`. O launcher confere MAC, hash do modelo selecionado, runtime e bibliotecas antes de executar. Configuração incorreta falha em vez de executar um perfil diferente silenciosamente.

A temperatura0, seed801 (802 na segunda repetição), cache_promptfalse e max_tokens128 são parâmetros de cada requisição, documentados no perfil. Os defaults genéricos do servidor não substituem esses campos. Prompt e esquema JSON devem ser fornecidos pelo controlador experimental. Esta preparação não implementa nem executa a bateria híbrida.

## Operação

No notebook, a partir desta pasta:

- `python3 select_host.py`: seleciona uma principal saudável; tenta reservas se nenhuma principal estiver disponível. Confere identidade e perfil ativo.
- `python3 select_host.py --reserve-only`: verifica as reservas.
- `python3 select_host.py --model 15`: verifica endpoints que estejam com o perfil1,5B ativo.

Nas placas, via SSH com sudo: `systemctl start smarthome-benchmark-15.service` ativa1,5B; `systemctl start smarthome-benchmark-05.service` volta ao padrão. Aguarde `/health` pronto e confira `/props` antes de enviar inferência.

As reservas têm0,5B carregado, mas não entram na distribuição normal. `pool.json` registra papéis, MACs e IPs atuais. Não se repete silenciosamente uma inferência despachada cujo resultado ficou incerto: preserve a tentativa, registre a falha e a eventual reatribuição. A seleção de reserva acontece antes do despacho; não é migração de uma inferência em andamento. IPs são DHCP: mudança de endereço exige redescoberta por MAC e atualização/revalidação do manifesto.

A interface8092 usa as cinco principais primeiro, seguidas das duas reservas, com o caminho comum do0,5B. Ela usa seu processo separado na porta19116, preservando os testes e avaliações anteriores. Não execute testes manuais concorrentes com medições formais no mesmo nó. A reserva só é tentada automaticamente em falha de preparação, não após timeout de inferência.

## Evidência

`inventory.json`: identificação e condições após reboot. `provisioning.json`: hashes e configuração instalada. `validation.json`: inferência curta de cada modelo em cada placa, com requisição e resposta; são verificações de execução, não acurácia. `recovery_test.json`: reinício automático após encerrar um processo e seleção de principal/reserva sob indisponibilidade controlada. `console_smoke.json`: verificação funcional da interface. Essas verificações não certificam ausência de falhas físicas futuras, não são resultados científicos e não alteram o estudo original.

Os demais hosts fornecidos estão fora deste pool porque não têm o runtime/modelos originais instalados. Nenhum dado de artigo ou modelo foi sobrescrito. A conferência do reboot completo e DHCP futuro pode ser repetida com o inventário e a validação; não há promessa de disponibilidade permanente.

## Resultado final

Sete placas passaram nos dois perfis (14 verificações de inferência). Todas terminaram com0,5B pronto e habilitado no boot. O processo da reserva lab4 foi encerrado deliberadamente: systemd reiniciou o serviço e a saúde voltou. Ao indisponibilizar a principal lab1, a seleção avançou para lab2; em um pool de teste sem outra principal disponível, escolheu a reserva lab4. Todas as sete foram restauradas ao final. O log de erros do kernel consultado após os testes não apresentou mensagens nas sete placas. Isso é uma verificação pontual de funcionamento, não teste de duração nem garantia de hardware.

A interface executou o smoke0,5B pela lab1 (.129) em21,01s e preservou as13 avaliações existentes, incluindo as quatro avaliações originais. Não foi registrada avaliação humana pelo agente.
