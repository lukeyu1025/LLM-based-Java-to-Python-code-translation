import os
from translation import run_CoT_translation_reflection

# === Paths ===
BASE_JAVA_DIR = "../codenet_project/Project_CodeNet_Java250"
DIRECT_DIR = "batch_translation/direct"
COT_VARIANT_DIR = "batch_translation/CoT_variant_reflection"

os.makedirs(COT_VARIANT_DIR, exist_ok=True)

# === create java source file path of direct translated code ===
direct_files = [f for f in os.listdir(DIRECT_DIR) if f.endswith("_dir.py")]

for file in direct_files:
    # Extract problem_id and submission_id
    base = file.replace("_dir.py", "")
    parts = base.split("_")
    if len(parts) != 2:
        continue

    problem_id, submission_id = parts
    java_path = os.path.join(BASE_JAVA_DIR, problem_id, f"{submission_id}.java")
    cot_out_path = os.path.join(COT_VARIANT_DIR, f"{problem_id}_{submission_id}_CoT.py")

    if not os.path.exists(java_path):
        print(f" Java file not found: {java_path}")
        continue

    print(f" Re-translating {java_path} -> {cot_out_path} (CoT only)")
    run_CoT_translation_reflection(java_path, cot_out_path)
