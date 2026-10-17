#!/bin/sh
set -e

echo "[*] Initializing Ollama daemon in background..."
ollama serve &
SERVER_PID=$!

echo "[*] Waiting for Ollama API endpoint to become responsive..."
until curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done

BASE_MODEL="llama3.2:3b"
CUSTOM_MODEL="resq-tactical:latest"

echo "[*] Ensuring base weights '${BASE_MODEL}' exist..."
ollama pull "${BASE_MODEL}"

if [ -f "/etc/ollama/Modelfile" ]; then
    echo "[*] Compiling custom tactical model '${CUSTOM_MODEL}' from Modelfile..."
    ollama create "${CUSTOM_MODEL}" -f /etc/ollama/Modelfile
fi

echo "[✓] Ollama Level 3 Tactical Service online and listening on 11434."
wait $SERVER_PID