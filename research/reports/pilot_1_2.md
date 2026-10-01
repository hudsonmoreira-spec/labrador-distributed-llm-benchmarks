# Proposta de piloto (não executado)

## Objetivo

Comparar uma requisição única em um nó e em dois nós usando o mesmo artefato, quantização, prompt e parâmetros. Só atende ao experimento distribuído se o runtime particionar o mesmo modelo entre processos/nós; duas réplicas independentes são outro experimento.

## Pendências

Nenhum runtime de LLM distribuído foi confirmado no inventário. Verificar em cada nó escolhido e no controlador a versão/commit, documentação do particionamento, transporte, formato de modelo e instrumentação. `llama.cpp`, Ollama, vLLM, MPI e `iperf3` estão ausentes em parte da bancada; não instalar ou iniciar nada nesta etapa.

## Comandos planejados

Após aprovar instalação/configuração, registrar `command -v`, `--version`, commit e documentação; copiar/verificar o mesmo hash do modelo e usar uma configuração explícita de dois workers. Executar primeiro o caso de controle em `node01`, depois o caso de dois nós em `node01,node02`, com o mesmo prompt fixo. O comando exato depende do runtime escolhido e não deve ser inventado antes dessa verificação.

## Evidência exigida

Guardar logs do launcher e de cada worker contendo node/IP, rank, PID, carregamento das mesmas camadas, hash do modelo, início/fim UTC e identificador da requisição. Confirmar no trace que os dois ranks participaram da mesma requisição. Sem essa evidência, classificar como réplica/encaminhamento, não como modelo particionado. Não prometer medição de sincronização sem instrumentação do runtime.
