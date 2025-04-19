import json
import os

input_path = "data/train/sec-new-desc.jsonl"
output_path = "data/ft-secure-code-combined.jsonl"

output_file = open(output_path, "w")

count = 0
with open(input_path, "r") as f:
    for line in f:
        row = json.loads(line)

        if not row["file_name"].endswith(".py"):
            continue  # Only use Python files

        description = row["description"].strip()
        secure_code = row["func_src_after"].strip()
        insecure_code = row["func_src_before"].strip()

        # ✅ Generation-style entry (prompt → secure code)
        gen_sample = {
            "messages": [
                {"role": "system", "content": "You are a secure Python code generation assistant."},
                {"role": "user", "content": description},
                {"role": "assistant", "content": secure_code}
            ]
        }
        output_file.write(json.dumps(gen_sample) + "\n")

        # ✅ Fixing-style entry (insecure → secure code)
        fix_sample = {
            "messages": [
                {"role": "system", "content": "You are a Python security assistant that rewrites insecure code."},
                {"role": "user", "content": f"Fix the following insecure code:\n\n{insecure_code}"},
                {"role": "assistant", "content": secure_code}
            ]
        }
        output_file.write(json.dumps(fix_sample) + "\n")

        count += 2

output_file.close()
print(f"✅ Saved {count} training examples to: {output_path}")