#Self refinement assume output is insecure from bandit, it will send it back to gpt due to the insecure code, generate it again, probably two iteration, if bandit is secure, output the code

from typing import List, Dict
from config import Config
from analyzer.bandit_scan import run_bandit
from generator.openai_gen import generate_code

def self_critique(code: str) -> List[str]:
    """
    Ask the model to list potential security issues in its own code.
    """
    critique_prompt = (
        "Review the following Python code and list any potential security "
        "issues as bullet points:\n```python\n"
        f"{code}\n```"
    )
    output = generate_code(critique_prompt)
    return [line.lstrip("- ").strip() for line in output.splitlines() if line.startswith("-")]

def self_fix(prompt: str, initial_code: str) -> str:
    """
    Iteratively fix code using Bandit + model self‐critique feedback.
    """
    code = initial_code
    for i in range(Config.MAX_FIX_ITER):
        bandit_issues = run_bandit(code)
        model_issues = self_critique(code) if i == 0 else []
        # merge into unified list of dicts
        combined: List[Dict] = bandit_issues + [
            {"issue_text": txt, "issue_severity": "self"} for txt in model_issues
        ]
        if not combined:
            return code, []

        feedback = "\n".join(f"- {iss['issue_text']}" for iss in combined)
        fix_prompt = (
            prompt
            + "\n\n# Fix these security issues:\n"
            + feedback
            + "\n\n# Original code:\n```python\n"
            + code
            + "\n```"
        )
        code = generate_code(fix_prompt)

    remaining = run_bandit(code)
    if remaining:
        print(f"⚠️ Self‑fix failed after {Config.MAX_FIX_ITER} rounds; issues remain:")
        for iss in remaining:
            print(f"  - {iss['issue_text']} (Severity: {iss['issue_severity']})")
        # you can choose to:
        #  • return the last attempt anyway
        #  • or raise RuntimeError("…")
        #  • or return initial_code
    return code, remaining
