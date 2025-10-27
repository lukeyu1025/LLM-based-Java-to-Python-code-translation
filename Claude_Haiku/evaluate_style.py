import os
import pandas as pd
import subprocess
import re

# translation path
translation_dirs = {
    "direct": "batch_translation/direct",
    "cot": "batch_translation/CoT"
}

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

# Evaluate all files
for strategy, folder in translation_dirs.items():
    if not os.path.exists(folder):
        continue
    for filename in os.listdir(folder):
        if filename.endswith(".py"):
            problem_id = filename.split("_")[0]
            full_path = os.path.join(folder, filename)
            score = get_pylint_score(full_path)
            results.append({
                "ProblemID": problem_id,
                "Strategy": strategy,
                "Filename": filename,
                "PylintScore": score
            })

# Save results
df = pd.DataFrame(results)
output_path = "batch_translation/style_pylint_results.csv"
df.to_csv(output_path, index=False)
