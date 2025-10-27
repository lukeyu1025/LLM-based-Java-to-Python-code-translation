import os
import pandas as pd
import subprocess
import re

# translated Python path
batch_dir = "batch_translation"
cot_variant_dir = os.path.join(batch_dir, "CoT_variant_reflection")

results = []

def get_pylint_score(file_path):
    try:
        result = subprocess.run(
            ["pylint", "--score=y", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout
        match = re.search(r'Your code has been rated at ([\d\.]+)/10', output)
        if match:
            return float(match.group(1))
        return None
    except subprocess.TimeoutExpired:
        return None

# evaluate CoT variant
if os.path.exists(cot_variant_dir):
    for filename in os.listdir(cot_variant_dir):
        if filename.endswith(".py"):
            problem_id = filename.split("_")[0]
            full_path = os.path.join(cot_variant_dir, filename)
            score = get_pylint_score(full_path)
            results.append({
                "ProblemID": problem_id,
                "Filename": filename,
                "PylintScore": score
            })

# Save results
df = pd.DataFrame(results)
out_path = os.path.join(batch_dir, "style_pylint_results_reflection.csv")
df.to_csv(out_path, index=False)
print(f" Pylint style evaluation saved to {out_path}")
