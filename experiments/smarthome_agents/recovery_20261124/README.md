# Recuperação do ambiente — 24/11/2026

Acesso administrativo e testes pela Ethernet 192.168.50.0/24.

## Placas identificadas com modelos

| Placa | IP | Situação |
|---|---|---|
| lab1 | 192.168.50.129 | SSH e serviço original 8080 prontos |
| lab2 | 192.168.50.89 | SSH e serviço original 8080 prontos |
| lab3 | 192.168.50.169 | SSH e serviço original 8080 prontos |
| lab4 reserva | 192.168.50.85 | SSH; modelos 0,5B e 1,5B disponíveis para a interface |
| lab7 | 192.168.50.240 | SSH e serviço original 8080 prontos |

A lab6 (último IP .200) e a lab8 original (.195) não foram reencontradas pelo MAC na varredura SSH. Há outras placas na rede, inclusive com nomes repetidos; não são substituições confirmadas desses equipamentos.

## Recuperação local

Os três serviços locais anteriores eram transitórios. Foram criadas unidades persistentes de usuário, habilitadas e iniciadas. Inicializam quando a sessão do usuário é iniciada; não foi configurado login automático ou linger.

- smarthome-review-console.service: interface 127.0.0.1:8092
- smarthome-model15-pc-original.service: 1,5B original no notebook, porta 19118
- smarthome-model15-local.service: 1,5B para modo híbrido, porta 19119

A interface aceita SMARTHOME_CONSOLE_HOSTS; nesta recuperação foi configurada apenas a reserva confirmada 192.168.50.85, evitando aguardar a reserva ausente .200. Ao alternar entre modelos na mesma placa, a interface carrega o modelo escolhido.

Os smoke-*.json registram chamadas novas de disponibilidade, separadas dos resultados do artigo. Concluir uma inferência não significa que a resposta esteja semanticamente correta. Nenhuma avaliação humana foi preenchida nesta recuperação.

Inventário bruto, integridade dos modelos conferida pela interface e resultados das chamadas estão neste diretório. Cópias das unidades estão em systemd-user/.

## Ajuste de recuperação

A primeira preparação do 1,5B na reserva excedeu o timeout SSH de 30 segundos durante sha256sum. O prazo dessa etapa foi aumentado para 180 segundos, sem remover a verificação de integridade. A falha inicial foi preservada em smoke-15.json; a nova tentativa é registrada separadamente.

## Resultado da verificação

- 0,5B na lab4: inferência concluída em 23,53 s.
- 1,5B original na lab4: inferência concluída em 60,27 s após ajustar o prazo de preparação.
- 1,5B original no notebook: inferência concluída em 6,98 s.
- Runtime do modo híbrido no notebook: resposta de teste recebida em 1,90 s.
- Ambos os modelos originais continuam apresentando respostas inadequadas ao comando português usado nesta verificação. Isso é distinto de indisponibilidade do serviço. Nenhuma melhoria de qualidade é alegada.
