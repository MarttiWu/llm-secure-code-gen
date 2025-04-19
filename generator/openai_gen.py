# generator/openai_gen.py

import os
import json
from config import Config
from openai import OpenAI
import re
from refinement.retrieval.faiss_retriever import FewShotRetriever

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

def generate_code(prompt: str, k_shots: int = 3, use_few_shot: bool = False) -> str:
    """Generate secure Python code using few-shot examples and structured output."""
    system_prompt = load_system_prompt()

    few_shot_text = ""
    if use_few_shot:
        retriever = FewShotRetriever()
        retriever.ensure_index_ready()

        few_shots = retriever.get_few_shots(prompt, k=k_shots)
        for ex in few_shots:
            few_shot_text += f"### Task:\n{ex['description']}\n"
            few_shot_text += f"### Solution:\n{ex['secure_code']}\n\n"

    final_prompt = few_shot_text + f"### Task:\n{prompt}\n### Solution:\n"

    try:
        # ✅ Structured output (GPT-4o+ only)
        response = client.responses.create(
            model=Config.get_model_name(),
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": final_prompt}
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

        try:
            fallback_response = client.chat.completions.create(
                model=Config.get_model_name(),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": final_prompt}
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