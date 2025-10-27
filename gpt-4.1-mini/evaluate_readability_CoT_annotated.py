import os
import pandas as pd
from radon.metrics import mi_visit

# translated Python path
batch_dir = "batch_translation"
cot_variant_dir = os.path.join(batch_dir, "CoT_variant_annotated")
results = []

def evaluate_readability(file_path):
    try:
        
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Maintainability Index (0-100)
        maintainability = mi_visit(code, True)

        return maintainability

    except Exception:
        return None

# compute MI for CoT variant
if os.path.exists(cot_variant_dir):
    for filename in os.listdir(cot_variant_dir):
        if filename.endswith(".py"):
            problem_id = filename.split("_")[0]
            full_path = os.path.join(cot_variant_dir, filename)
            mi_score = evaluate_readability(full_path)
            results.append({
                "ProblemID": problem_id,
                "Strategy": "cot_structured_summary",
                "Filename": filename,
                "MaintainabilityIndex": mi_score,
            })

# Save to CSV
df = pd.DataFrame(results)
out_path = os.path.join(batch_dir, "readability_results_annotated.csv")
df.to_csv(out_path, index=False)
print(f" Readability results saved to: {out_path}")
