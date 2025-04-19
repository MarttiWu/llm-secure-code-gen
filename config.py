# config.py

import os
from dotenv import load_dotenv

# load .env from project root
load_dotenv()
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    MODEL_NAME = "gpt-4o-mini-2024-07-18"

    TOKEN_LIMIT = 512

    SYSTEM_PROMPT_PATH = "prompts/system_prompt.txt"

    USE_SELF_FIX = True

    MAX_FIX_ITER = 2