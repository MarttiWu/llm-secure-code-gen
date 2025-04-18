# data/loader.py

import json

def load_dataset(path, limit=None):
    samples = []

    with open(path, "r") as f:
        for i, line in enumerate(f):
            if limit and len(samples) >= limit:
                break
            row = json.loads(line)

            if row.get("file_name", "").endswith(".py"):
                samples.append({
                    "description": row["description"],
                    "secure_code": row["func_src_after"],
                    "insecure_code": row["func_src_before"],
                    "vul_type": row.get("vul_type", "unknown"),
                    "file_name": row["file_name"],
                    "commit_msg": row["commit_msg"]
                })
    return samples