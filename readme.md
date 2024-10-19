## Whatsapp Ollama Integration
As I've setted up Ollama and open-webui on my homelab, this is just a simple script to chat with Ollama via Whatsapp.

## Environment Variables
| Key    | Value |
| -------- | ------- |
| WHATSAPP_URL | Whatsapp api url |
| WHATSAPP_SESSION | Whatsapp session |
| WHATSAPP_CHAT_ID | Whatsapp grout chat id |
| WHATSAPP_NUMBER_ID | Whatsapp number id |
| OLLAMA_URL | Ollama url |
| OLLAMA_TOKEN | Whatsapp session |
| OLLAMA_MODEL | Ollama model |
| LOG_LEVEL | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |


## Running with docker
```
docker run \
    -e WHATSAPP_URL=http://localhost \
    -e WHATSAPP_SESSION=ABC \
    -e WHATSAPP_CHAT_ID=12345678@g.us \
    -e WHATSAPP_NUMBER_ID=12345678@c.us \
    -e OLLAMA_URL=http://localhost \
    -e LOG_LEVEL=INFO \
    -e OLLAMA_MODEL=llama3.2:1b
    -e OLLAMA_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyzxyzxyz \ 
    aleixolucas/ollama_wpp_integration
```

## REF
- https://docs.openwebui.com/api/
- https://ollama.com
