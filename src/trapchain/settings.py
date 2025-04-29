# src/trapchain/settings.py
import os

LOKI_URL          = os.getenv("LOKI_URL", "http://localhost:3100")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your environment")

# Tune for your model’s context limit
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1500))

MODEL_NAME = "gpt-4.1-nano"
