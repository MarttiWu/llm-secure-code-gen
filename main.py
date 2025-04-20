import os
from datetime import datetime
from generator.openai_gen import generate_code
from analyzer.bandit_scan import run_bandit
from config import Config
from data.loader import load_dataset
from refinement.self_fix import self_fix
import argparse

def print_issues(issues, log_file):
    log_file.write("\n🛑 Security issues found:\n")
    for issue in issues:
        log_file.write(f"🔸 {issue.get('issue_text')} (Severity: {issue.get('issue_severity')})\n")

def main():
    parser = argparse.ArgumentParser(description="Secure Code Generator with optional few-shot")
    parser.add_argument("--few-shot", action="store_true", help="Enable few-shot prompting from training data")
    parser.add_argument("--use-ft", action="store_true", help="Use fine-tuned model")
    parser.add_argument("--use-self-fix", action="store_true", help="Use self-fix model")
    args = parser.parse_args()

    use_few_shot = args.few_shot
    use_self_fix = args.use_self_fix

    print("🔐 Secure Code Generator — Running...\n")
    print(f"📌 Few-shot mode: {'enabled' if use_few_shot else 'disabled'}\n")
    
    if args.use_ft:
        Config.USE_FINE_TUNED_MODEL = True
    print(f"🧠 Using model: {Config.get_model_name()}")

    # Load dataset
    dataset_path = "data/val/sec-new-desc.jsonl"
    samples = load_dataset(dataset_path, limit=50)

    # Prepare log file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"run_{timestamp}.log")

    secure_count = 0

    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"📄 Evaluation Log — {timestamp}\n")
        log_file.write("=" * 60 + "\n")

        for i, sample in enumerate(samples):
            prompt = sample["description"]
            log_file.write(f"\n================= 🔢 Sample {i + 1} =================\n")
            log_file.write(f"📝 Prompt: {prompt}\n")

            # Generate code
            code = generate_code(prompt, use_few_shot=use_few_shot)
            log_file.write("\n🤖 Generated Code:\n" + "-" * 40 + "\n")
            log_file.write(code + "\n")
            log_file.write("-" * 40 + "\n")

            # Evaluate with Bandit
            issues = run_bandit(code)

            if not issues:
                secure_count += 1
                log_file.write("✅ Code is secure.\n\n")
            else:
                if use_self_fix:
                    code, remaining = self_fix(prompt, code)
                if remaining:
                    
                    print_issues(issues, log_file)
                    log_file.write("❌ Code flagged as insecure.\n\n")
                else:
                    secure_count += 1
                    log_file.write("✅ Code is secure.\n\n")
            # Log ground truth
            log_file.write("📌 Ground Truth (from dataset):\n")
            log_file.write(sample["secure_code"] + "\n")
            log_file.write("=" * 60 + "\n")

    # ✅ Terminal output only: summary
    print(f"✅ {secure_count}/{len(samples)} generated samples are secure.")

if __name__ == "__main__":
    main()