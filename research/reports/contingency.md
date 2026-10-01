# Procedimento de contingência

1. Marcar a execução como `interrompida_por_falha`, preservando logs, UTC, commit, modelo, quantização, prompt, configuração e grupo.
2. Registrar node/IP/MAC, sintoma, horário UTC, último log e diagnóstico; não substituir silenciosamente.
3. Selecionar a primeira reserva elegível, verificar SSH, sudo, versão de sistema/runtime, modelo, quantização, configuração e estado de carga.
4. Registrar `substituicao: antiga -> reserva`, motivo e horário UTC no manifesto da execução.
5. Recomeçar a execução afetada desde o início. Avaliar, com o responsável pelo experimento, se os grupos anteriores precisam ser repetidos para manter pareamento e comparabilidade.
6. Se houver erro de identidade, armazenamento, rede ou temperatura, retirar o nó da bancada até investigação; não corrigir automaticamente.
