import os
import sys
from translation import run_translation

# === Paths ===
BASE_JAVA_DIR = "../codenet_project/Project_CodeNet_Java250"
OUT_DIR_DIRECT = "batch_translation/direct"
OUT_DIR_COT = "batch_translation/CoT"

os.makedirs(OUT_DIR_DIRECT, exist_ok=True)
os.makedirs(OUT_DIR_COT, exist_ok=True)

def translate_single(submission_code):
    try:
        problem_id, submission_id = submission_code.split("_")
    except ValueError:
        print(" Invalid format. Use: p0002_s003798551")
        return

    java_file = f"{submission_id}.java"
    java_path = os.path.join(BASE_JAVA_DIR, problem_id, java_file)

    if not os.path.exists(java_path):
        print(f" Java file not found at: {java_path}")
        return

    out_direct = os.path.join(OUT_DIR_DIRECT, submission_code + "_dir.py")
    out_cot = os.path.join(OUT_DIR_COT, submission_code + "_CoT.py")

    print(f" Translating {java_path}...")
    run_translation(java_path, out_direct, out_cot)
    print(f" Saved to {out_direct} and {out_cot}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python single_translation.py <problem_submission_id>")
        print("Example: python single_translation.py p00002_s003798551")
    else:
        translate_single(sys.argv[1])
