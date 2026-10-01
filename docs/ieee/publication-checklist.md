# Checklist antes da publicação

O material atual é útil para auditoria interna, mas não deve ser publicado sem revisão de privacidade e de completude.

- [ ] Remover ou pseudonimizar IPs, nomes de host, `machine-id`, MACs, números de série e caminhos de usuário.
- [ ] Revisar `research/data/ssh/known_hosts/` e qualquer log SSH antes do commit público.
- [ ] Confirmar que não há chaves privadas, tokens, senhas ou credenciais nos logs.
- [ ] Fixar um identificador de release/commit para o artefato suplementar.
- [ ] Adicionar versão do hardware, sistema operacional, runtime, modelo e quantização ao manifesto de cada benchmark.
- [ ] Adicionar scripts que regenerem cada tabela e figura a partir dos dados publicados.
- [ ] Documentar critérios de inclusão/exclusão, falhas e repetições.
- [ ] Separar claramente inventário preliminar de resultados de inferência.
- [ ] Revisar licenças de modelos, datasets, dependências e ferramentas de terceiros.

A sanitização deve produzir uma cópia pública dos dados; os dados internos originais devem permanecer fora do repositório público e sob controle do responsável pela bancada.
