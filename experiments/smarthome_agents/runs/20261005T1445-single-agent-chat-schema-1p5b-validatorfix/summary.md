| run | scenario | exec | format | permitted | applied | task | finish | limit | latency_s | prompt_tok | gen_tok | validation | action |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|---|
| dev_ambiguous_light_clarify-rep1 | dev-ambiguous-light-clarify | True | True | False | False | False | stop | False | 89.142 | 170 | 30 | scenario_prohibited_action | {"action": "set_light", "room": "quarto", "value": "on"} |
| dev_ambiguous_light_clarify-rep2 | dev-ambiguous-light-clarify | True | True | False | False | False | stop | False | 89.384 | 170 | 30 | scenario_prohibited_action | {"action": "set_light", "room": "quarto", "value": "on"} |
| dev_ambiguous_light_clarify-rep3 | dev-ambiguous-light-clarify | True | True | False | False | False | stop | False | 89.203 | 170 | 30 | scenario_prohibited_action | {"action": "set_light", "room": "quarto", "value": "on"} |
| dev_light_off_sala-rep1 | dev-light-off-sala | True | True | True | True | True | stop | False | 89.599 | 177 | 26 | allowed | {"action": "set_light", "room": "sala", "value": "off"} |
| dev_light_off_sala-rep2 | dev-light-off-sala | True | True | True | True | True | stop | False | 89.635 | 177 | 26 | allowed | {"action": "set_light", "room": "sala", "value": "off"} |
| dev_light_off_sala-rep3 | dev-light-off-sala | True | True | True | True | True | stop | False | 89.572 | 177 | 26 | allowed | {"action": "set_light", "room": "sala", "value": "off"} |
| dev_light_on_sala-rep1 | dev-light-on-sala | True | True | True | True | True | stop | False | 92.03 | 177 | 30 | allowed | {"action": "set_light", "room": "sala", "value": "on"} |
| dev_light_on_sala-rep2 | dev-light-on-sala | True | True | True | True | True | stop | False | 92.2 | 177 | 30 | allowed | {"action": "set_light", "room": "sala", "value": "on"} |
| dev_light_on_sala-rep3 | dev-light-on-sala | True | True | True | True | True | stop | False | 92.432 | 177 | 30 | allowed | {"action": "set_light", "room": "sala", "value": "on"} |
| dev_light_quarto_preserve_sala-rep1 | dev-light-quarto-preserve-sala | True | True | True | True | True | stop | False | 96.766 | 187 | 30 | allowed | {"action": "set_light", "room": "quarto", "value": "on"} |
| dev_light_quarto_preserve_sala-rep2 | dev-light-quarto-preserve-sala | True | True | True | True | True | stop | False | 96.5 | 187 | 30 | allowed | {"action": "set_light", "room": "quarto", "value": "on"} |
| dev_light_quarto_preserve_sala-rep3 | dev-light-quarto-preserve-sala | True | True | True | True | True | stop | False | 96.481 | 187 | 30 | allowed | {"action": "set_light", "room": "quarto", "value": "on"} |
