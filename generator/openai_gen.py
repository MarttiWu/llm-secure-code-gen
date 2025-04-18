# generator/openai_gen.py

import os
import json
from config import Config
from openai import OpenAI
import re

# Initialize the OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)

def load_system_prompt():
    """Load the system prompt from a file, or use default fallback."""
    try:
        with open(Config.SYSTEM_PROMPT_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a secure Python coding assistant. Only respond with valid Python code."

def extract_raw_code(text):
    """Extract code from markdown-style responses, as fallback."""
    match = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return match[0].strip() if match else text.strip()

def generate_code(prompt: str) -> str:
    """Generate secure Python code using structured outputs (JSON Schema)."""
    system_prompt = load_system_prompt()

    try:
        response = client.responses.create(
            model=Config.MODEL_NAME,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "secure_python_code",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "language": {"type": "string", "enum": ["python"]},
                            "code": {"type": "string"}
                        },
                        "required": ["language", "code"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )

        result = json.loads(response.output_text)
        return result["code"]

    except Exception as e:
        print(f"⚠️ Structured output failed: {type(e).__name__}: {e}")
        print("🔁 Falling back to classic generation...\n")

        # Fallback to plain completion (older models or SDK)
        try:
            fallback_response = client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=Config.TOKEN_LIMIT,
                temperature=0.7,
                top_p=0.9
            )
            output = fallback_response.choices[0].message.content
            return extract_raw_code(output)
        except Exception as inner_e:
            print(f"❌ Fallback failed too: {type(inner_e).__name__}: {inner_e}")
            return "# Error generating code"