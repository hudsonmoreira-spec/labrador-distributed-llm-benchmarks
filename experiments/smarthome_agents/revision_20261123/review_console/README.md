# Interface local de avaliação SmartHome

Abrir http://127.0.0.1:8092 no notebook. O serviço de usuário `smarthome-review-console.service` está ativo nesta sessão; reinicia em caso de falha. Desde 24/11, está habilitado para iniciar ao entrar na sessão do usuário; ver `../../recovery_20261124/systemd-user/`. Para iniciar manualmente: `python3 app.py`, a partir desta pasta.

A aba **Testar um comando** recebe texto, estados iniciais, localização conhecida ou desconhecida e escolha entre Qwen 0,5B e 1,5B. A inferência real usa uma reserva Labrador via Ethernet, porta isolada 19116, contexto512, quatro threads, seed801, temperature0 e o prompt/esquema originais. Não oferece o avaliador ou respostas esperadas ao modelo. A proposta passa pelo executor original. Falha de infraestrutura não recebe julgamento de qualidade. Na preparação, tenta a outra reserva se necessário; após despacho não repete silenciosamente uma requisição cujo resultado é incerto.

A aba **Revisar os 4 casos do artigo** lê requisições e respostas originais, sem reexecutá-las e sem mostrar como sugestão o julgamento assistido anterior. O usuário escolhe Sim, Não ou Não sei; Não requer justificativa e Não sei mantém pendência. Nome do avaliador é autodeclarado no formulário local. A interface não autentica a identidade do revisor.

`records/<uuid>/` contém cada novo teste: entrada, requisição, resposta, configuração do runtime e resultado. `records/reviews/` contém avaliações explícitas, com data, nome, critério, decisão, justificativa e hashes das fontes. Cada gravação cria um novo arquivo; revisões anteriores e arquivos científicos originais são preservados. O botão de download exporta as avaliações em JSON. Novos testes não são incorporados aos 240 resultados reservados do artigo. A interface não edita automaticamente o manuscrito ou encerra suas pendências.

Validação: três testes de integridade/persistência passaram usando pasta temporária e nomes de fixture; nenhuma avaliação humana fictícia foi gravada nos registros reais. Um envio pelo navegador executou Qwen0,5B na lab4 (.85) em aproximadamente20s, e exibiu a proposta, bloqueio pelo executor, estado final e formulário de avaliação. Os quatro casos originais e a recuperação de um resultado após reinício do servidor foram conferidos. O processo de IA da interface permanece disponível para o próximo comando, separado dos serviços existentes.

## Novo modo híbrido

Está disponível a opção **Qwen1,5B + regras · notebook**; o padrão atual é **Qwen1,5B original · notebook**. A IA classifica intenção; regras validam escopo/cômodo e produzem a ação. A interface diferencia a origem, guarda as chamadas de intenção e identifica a configuração `hybrid_intent_v2`. Os modos originais e avaliações anteriores foram preservados. Ver `../model15_adjustment/README.md` para evidências, testes e limites. O novo modo utiliza somente o notebook e não precisa alcançar uma Labrador por SSH.

## Comparação direta de hardware

A opção **Qwen1,5B original · notebook** executa o prompt/esquema originais, contexto512 e quatro threads, sem regras híbridas que construam a resposta. As propostas continuam passando pelo executor simulado e a ação/resposta bruta ficam registradas. O serviço é `smarthome-model15-pc-original.service` (loopback19118). Ver `../hardware_comparison/COMPARISON.md` para os oito pares de respostas e limites da conclusão.

## Avaliação dos registros originais concluída

Em 24/11, Hudson salvou as quatro avaliações originais como inadequadas, com justificativas. O pacote separado `../author_review_20261124/` documenta procedimento, limites e verificação. Os novos testes interativos continuam separados dos resultados do artigo. `withdrawn_reviews/` preserva uma avaliação retirada explicitamente pelo autor por ter sido registrada no teste errado; ela não conta como avaliação ativa.
