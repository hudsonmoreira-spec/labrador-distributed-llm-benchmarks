# Resident Server Configuration 2026-10-05

This configuration supports the corrected single-agent pilot only. It is not a frozen main-campaign protocol.

## Host and Service

- Host: `192.168.50.89` (`lab2`).
- Service directory: `/home/caninos/smarthome_agents/single_agent_1p5b/`.
- Port: `18089`.
- Existing unrelated server on port `8080` was left unchanged.
- Startup command:

```bash
/home/caninos/llama-offline/llama.cpp/build/bin/llama-server \
  --model /home/caninos/models/qwen2.5-1.5b-instruct-q5_k_m.gguf \
  --host 0.0.0.0 \
  --port 18089 \
  --threads 4 \
  --ctx-size 1024 \
  --n-predict 96 \
  --parallel 1 \
  --metrics
```

The server became healthy after 72 seconds, measured by polling `http://127.0.0.1:18089/health` from the Labrador.

## Runtime

- Runtime binary: `/home/caninos/llama-offline/llama.cpp/build/bin/llama-server`.
- Runtime version: `version: 9584 (e25a32e98)`.
- Build line: `built with GNU 12.2.0 for Linux aarch64`.
- The runtime is used from a single existing build tree to avoid mixing binaries and libraries.

## Model

- Local model file: `/home/caninos/models/qwen2.5-1.5b-instruct-q5_k_m.gguf`.
- SHA-256: `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`.
- Quantization, inferred from filename: `Q5_K_M`.
- Upstream base model: `Qwen/Qwen2.5-1.5B-Instruct`.
- Upstream license recorded from the Hugging Face model card: Apache-2.0.
- Local GGUF conversion source is not yet proven from primary metadata; this remains a documentation gap before protocol freeze.

## Request Parameters

- Corrected endpoint: `/v1/chat/completions`.
- Previous development endpoint `/completion` is preserved only in older smoke/campaign logs.
- Chat template: supplied by the Qwen GGUF metadata and exposed through `GET /props`; the template uses Qwen `<|im_start|>system`, `<|im_start|>user`, and `<|im_start|>assistant` message formatting.
- Structured output: `response_format` with `type: json_schema` and nested `json_schema.schema`.
- Temperature: `0`.
- Seeds in the schema-constrained 12-run pilot: `601`, `602`, `603`, repeated per scenario.
- `max_tokens`: `128` per request in the schema-constrained pilot. The earlier 48-token budget was too small and contributed to truncated or repeated outputs.
- Prompt cache in request payload: `false`.
- The server remains resident across requests. The campaign logs and server elapsed time confirm the process was not restarted between the 12 requests.

The llama.cpp server documentation describes `/v1/chat/completions` as an OpenAI-compatible endpoint and documents `response_format` for plain JSON and schema-constrained JSON. The local server was also tested directly before the campaign; the non-nested `response_format: {"type":"json_schema","schema":...}` shape was not sufficient on this installation, while `response_format: {"type":"json_schema","json_schema":{"name":"smart_home_action","strict":true,"schema":...}}` produced schema-shaped output.

## Memory Collection

Memory was collected using:

```bash
ps -o pid,rss,vsz,pcpu,pmem,etime,args -p $(cat /home/caninos/smarthome_agents/single_agent_1p5b/server.pid)
```

The corrected 12-run campaign stores `memory_before.txt` and `memory_after.txt` beside every attempt. A final check at `2026-10-05T13:47:14Z` reported RSS `1287848` KiB and `%MEM` `64.8`.
