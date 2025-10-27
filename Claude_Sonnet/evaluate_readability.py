
import os
import pandas as pd
from radon.metrics import mi_visit

# translated Python path
translation_dirs = {
    "direct": "batch_translation/direct",
    "cot": "batch_translation/CoT"
}

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

# compute MI for all both Dir and CoT translation
for strategy, folder in translation_dirs.items():
    if not os.path.exists(folder):
        continue
    for filename in os.listdir(folder):
        if filename.endswith(".py"):
            problem_id = filename.split("_")[0]
            full_path = os.path.join(folder, filename)
            mi_score = evaluate_readability(full_path)
            results.append({
                "ProblemID": problem_id,
                "Strategy": strategy,
                "Filename": filename,
                "MaintainabilityIndex": mi_score,
            })

# Save to CSV
df = pd.DataFrame(results)
output_path = "batch_translation/readability_results.csv"
df.to_csv(output_path, index=False)
