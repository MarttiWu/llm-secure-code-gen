import os
from dotenv import load_dotenv

# load .env from project root
load_dotenv()
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    USE_FINE_TUNED_MODEL = False
    FINE_TUNED_MODEL_NAME = "ft:gpt-4o-mini-2024-07-18:secure-code-gen-lab:secure-code-gen-v1:BNtINMe2"
    DEFAULT_MODEL_NAME = "gpt-4o-mini-2024-07-18"
    
    TOKEN_LIMIT = 1024
    SYSTEM_PROMPT_PATH = "prompts/system_prompt.txt"
    MAX_FIX_ITER = 2
    @classmethod
    def get_model_name(cls):
        return cls.FINE_TUNED_MODEL_NAME if cls.USE_FINE_TUNED_MODEL else cls.DEFAULT_MODEL_NAME

    USE_SELF_FIX = True