import os
import random
from translation import run_translation

# === input output path ===

BASE_JAVA_DIR = "../codenet_project/Project_CodeNet_Java250"
OUT_DIR_DIRECT = "batch_translation/direct"
OUT_DIR_COT = "batch_translation/CoT"

os.makedirs(OUT_DIR_DIRECT, exist_ok=True)
os.makedirs(OUT_DIR_COT, exist_ok=True)

# === get unique problem ID===
def get_valid_problem_ids(base_path):
    problem_ids = []
    for pid in os.listdir(base_path):
        problem_path = os.path.join(base_path, pid)
        if os.path.isdir(problem_path):
            files = [f for f in os.listdir(problem_path) if f.endswith(".java")]
            if files:
                problem_ids.append((pid, files))
    return problem_ids

# === Step 1: Sample n random valid problems ===
valid_problems = get_valid_problem_ids(BASE_JAVA_DIR)
sampled = random.sample(valid_problems, 20)

# === Step 2: Run translation ===
for pid, java_files in sampled:
    filename = java_files[0]  
    java_path = os.path.join(BASE_JAVA_DIR, pid, filename)

    # e.g., p0002_s003798551
    base_name = f"{pid}_{filename.replace('.java', '')}"

    out_direct = os.path.join(OUT_DIR_DIRECT, base_name + "_dir.py")
    out_cot = os.path.join(OUT_DIR_COT, base_name + "_CoT.py")

    print(f"Translating {java_path} -> {out_direct}, {out_cot}")
    run_translation(java_path, out_direct, out_cot)  # defined in translation.py
