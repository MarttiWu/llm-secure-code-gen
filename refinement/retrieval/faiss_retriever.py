# retrieval/faiss_retriever.py

import json
import faiss
import os
from sentence_transformers import SentenceTransformer
import numpy as np

INDEX_PATH = "retrieval/faiss_index"
DATA_PATH = "data/train/sec-new-desc.jsonl"
EMBED_MODEL = "all-MiniLM-L6-v2"

class FewShotRetriever:
    def __init__(self, index_path=INDEX_PATH, data_path=DATA_PATH):
        self.index_path = index_path
        self.data_path = data_path
        self.model = SentenceTransformer(EMBED_MODEL)
        self.index = None
        self.examples = []
        
    def ensure_index_ready(self):
        if not os.path.exists(self.index_path):
            self.build_index()
        else:
            self.load_index()

    def build_index(self):
        print("🔄 Building FAISS index from training data...")

        with open(self.data_path, "r") as f:
            for line in f:
                row = json.loads(line)
                if row.get("file_name", "").endswith(".py"):
                    self.examples.append({
                        "description": row["description"],
                        "secure_code": row["func_src_after"]
                    })

        descriptions = [ex["description"] for ex in self.examples]
        embeddings = self.model.encode(descriptions, convert_to_numpy=True)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        # ✅ Create folder if needed
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        faiss.write_index(self.index, self.index_path)
        print(f"✅ Saved FAISS index to {self.index_path}")

    def load_index(self):
        if not os.path.exists(self.index_path):
            raise FileNotFoundError("Index not found. Run build_index() first.")
        self.index = faiss.read_index(self.index_path)

        # Load the original examples again (in same order!)
        self.examples = []
        with open(self.data_path, "r") as f:
            for line in f:
                row = json.loads(line)
                if row.get("file_name", "").endswith(".py"):
                    self.examples.append({
                        "description": row["description"],
                        "secure_code": row["func_src_after"]
                    })

    def get_few_shots(self, query: str, k: int = 3):
        if self.index is None:
            self.load_index()

        query_vec = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_vec, k)

        few_shots = []
        for idx in indices[0]:
            ex = self.examples[idx]
            few_shots.append(ex)

        return few_shots