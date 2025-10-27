import os
import ast
import csv
import pandas as pd

# CoT variant path
batch_dir = "batch_translation"
cot_variant_dir = os.path.join(batch_dir, "CoT_variant_reflection")
# Check Python syntax with Python ast
def check_syntax(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True
    except SyntaxError:
        return False

# combine results
results = []
for filename in os.listdir(cot_variant_dir):
    if filename.endswith(".py"):
        full_path = os.path.join(cot_variant_dir, filename)
        passed = check_syntax(full_path)
        problem_id = filename.split("_")[0]
        results.append({
            "ProblemID": problem_id,
            "Filename": filename,
            "SyntaxPassed": passed
        })

# save results
csv_path = os.path.join(batch_dir, "syntax_results_reflection.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["ProblemID", "Filename", "SyntaxPassed"])
    writer.writeheader()
    writer.writerows(results)
print(f"Syntax check completed. Results saved to {csv_path}")