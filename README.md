# Secure Code Generation with LLMs

This project builds a secure code generation pipeline using Large Language Models (LLMs), static analysis, and self-reflection. The system takes natural language prompts and generates secure Python code, filtering and refining it before output using Bandit and self-correction techniques.

---

## Features

- **Natural Language to Secure Code**: Generate Python code from plain English prompts
- **Fine-Tuned LLMs**: Optionally use OpenAI fine-tuned models for better security-awareness
- **Few-Shot Prompting**: Retrieve and insert relevant training examples using FAISS similarity search
- **Static Analysis**: Use Bandit to detect insecure code patterns before returning output
- **Self-Reflection Loop**: Iteratively correct insecure outputs using feedback and self-critique

---

## Usage

### 1. Setup

```bash
conda create -n secure-code-gen python=3.10
conda activate secure-code-gen
pip install -r requirements.txt
```

Ensure your OpenAI API key is set:
```bash
export OPENAI_API_KEY=your-key-here
```

### 2. Build Few-Shot Index
```bash
python build_faiss_index.py
```

### 3. Run Inference
```bash
python main.py --few-shot --use-ft --use-self-fix
```
