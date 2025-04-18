# analyzer/bandit_scan.py

import subprocess
import json
import tempfile
from typing import List, Dict

def run_bandit(code_snippet: str) -> List[Dict]:
    """
    Run Bandit static analysis on a Python code snippet.
    Returns a list of security issues found.
    """
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as tmp_file:
        tmp_file.write(code_snippet)
        tmp_file.flush()
        tmp_path = tmp_file.name

    try:
        result = subprocess.run(
            ["bandit", "-r", tmp_path, "-f", "json"],
            capture_output=True,
            text=True
        )

        output = json.loads(result.stdout)
        issues = output.get("results", [])

        return issues

    except FileNotFoundError:
        print("❗ Bandit is not installed or not available in PATH.")
        return [{"issue_text": "Bandit not found", "issue_severity": "HIGH"}]

    except json.JSONDecodeError:
        print("❗ Bandit output could not be parsed.")
        return [{"issue_text": "Invalid Bandit output", "issue_severity": "HIGH"}]