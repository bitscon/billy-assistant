#!/bin/sh
export OLLAMA_HOST=0.0.0.0:11434
exec /bin/ollama serve
