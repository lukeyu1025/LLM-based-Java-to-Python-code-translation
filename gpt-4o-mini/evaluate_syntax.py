import os
import ast
import csv
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# translated file path
base_dir = "batch_translation"
folders = {
    "direct": os.path.join(base_dir, "direct"),
    "cot": os.path.join(base_dir, "CoT")
}

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
for strategy, folder in folders.items():
    for filename in os.listdir(folder):
        if filename.endswith(".py"):
            full_path = os.path.join(folder, filename)
            passed = check_syntax(full_path)
            problem_id = filename.split("_")[0]
            results.append({
                "ProblemID": problem_id,
                "Filename": filename,
                "Strategy": strategy,
                "SyntaxPassed": passed
            })

# save results
csv_path = os.path.join(base_dir, "syntax_results.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["ProblemID", "Filename", "Strategy", "SyntaxPassed"])
    writer.writeheader()
    writer.writerows(results)

print(f"Syntax check completed. Results saved to {csv_path}")

# === analyze summary ===
by_id = defaultdict(lambda: {"direct": False, "cot": False})
for row in results:
    by_id[row["ProblemID"]][row["Strategy"]] = row["SyntaxPassed"]

summary = {
    "both_pass": 0,
    "both_fail": 0,
    "direct_pass_cot_fail": 0,
    "direct_fail_cot_pass": 0
}

for status in by_id.values():
    if status["direct"] and status["cot"]:
        summary["both_pass"] += 1
    elif not status["direct"] and not status["cot"]:
        summary["both_fail"] += 1
    elif status["direct"] and not status["cot"]:
        summary["direct_pass_cot_fail"] += 1
    elif not status["direct"] and status["cot"]:
        summary["direct_fail_cot_pass"] += 1

# save results to csv
summary_df = pd.DataFrame([
    {"Category": "both_pass", "Count": summary["both_pass"]},
    {"Category": "both_fail", "Count": summary["both_fail"]},
    {"Category": "direct_pass_cot_fail", "Count": summary["direct_pass_cot_fail"]},
    {"Category": "direct_fail_cot_pass", "Count": summary["direct_fail_cot_pass"]}
])
summary_csv = os.path.join(base_dir, "syntax_category_summary.csv")
summary_df.to_csv(summary_csv, index=False)
print(f"Syntax category summary saved to {summary_csv}")

# Plot bar chart
labels = ["Both Pass", "Both Fail", "Direct Pass, CoT Fail", "Direct Fail, CoT Pass"]
values = [
    summary["both_pass"],
    summary["both_fail"],
    summary["direct_pass_cot_fail"],
    summary["direct_fail_cot_pass"]
]

plt.figure(figsize=(10, 6))
plt.bar(labels, values, color="#4e79a7")
plt.ylabel("Number of Problem IDs")
plt.title("Syntax Check Result Comparison (Direct vs CoT)")
plt.xticks(rotation=15)
plt.tight_layout()
plot_path = os.path.join(base_dir, "syntax_comparison_plot.png")
plt.savefig(plot_path)
print(f"Syntax comparison plot saved to {plot_path}")
