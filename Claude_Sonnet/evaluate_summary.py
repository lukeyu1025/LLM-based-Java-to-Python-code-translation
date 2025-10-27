import pandas as pd
import matplotlib.pyplot as plt

# Load all evaluation results
syn_df = pd.read_csv("batch_translation/syntax_results.csv")
func_df = pd.read_csv("batch_translation/functionality_results.csv")
sem_df = pd.read_csv("batch_translation/semantic_accuracy_results.csv")
read_df = pd.read_csv("batch_translation/readability_results.csv")
style_df = pd.read_csv("batch_translation/style_pylint_results.csv")

# === strategy labels ===
strategy_map = {"direct": "Direct", "cot": "CoT", "CoT": "CoT", "Cot": "CoT"}
syn_df["Strategy"] = syn_df["Strategy"].str.strip().str.casefold().map(strategy_map)
sem_df["strategy"] = sem_df["strategy"].str.strip().str.casefold().map(strategy_map)
read_df["Strategy"] = read_df["Strategy"].str.strip().str.casefold().map(strategy_map)
style_df["Strategy"] = style_df["Strategy"].str.strip().str.casefold().map(strategy_map)

# === Syntactic Correctness ===
total_by_strategy = syn_df.groupby("Strategy")["SyntaxPassed"].count()
passed_by_strategy = syn_df[syn_df["SyntaxPassed"] == True].groupby("Strategy")["SyntaxPassed"].count()
syntax_norm = (passed_by_strategy / total_by_strategy).to_dict()

# === Functionality ===

# Filter out invalid rows (skip any row where passed < 0)
filtered_func_dir_df = func_df[func_df["direct_passed"] >= 0].copy()
filtered_func_cot_df = func_df[func_df["cot_passed"] >= 0].copy()

# === ratio of Dir and CoT that passed ===
filtered_func_dir_df["direct_ratio"] = filtered_func_dir_df["direct_passed"] / filtered_func_dir_df["total"]
filtered_func_cot_df["cot_ratio"] = filtered_func_cot_df["cot_passed"] / filtered_func_cot_df["total"]

# === average to normalize ratio ===
func_norm = {
    "Direct": filtered_func_dir_df["direct_ratio"].mean(),
    "CoT": filtered_func_cot_df["cot_ratio"].mean()
}

# === Semantic Accuracy ===
sem_norm = sem_df.groupby("strategy")["semantic_match"].apply(lambda x: (x.str.lower() == "yes").mean()).to_dict()

# === Redability normalized ===
read_norm = read_df.groupby("Strategy")["MaintainabilityIndex"].mean().div(100).to_dict()

# === Style normalized ===
style_norm = style_df.groupby("Strategy")["PylintScore"].mean().div(10).to_dict()

# === Combine result ===
summary_df = pd.DataFrame({
    "Syntactic Correctness": syntax_norm,
    "Functionality Score": func_norm,
    "Semantic Accuracy": sem_norm,
    "Readability (MI)": read_norm,
    "Style (Pylint)": style_norm
}).T

# Save summary to CSV
summary_df.to_csv("batch_translation/evaluation_summary.csv")

print(summary_df)

# --- Plot ---
summary_df.plot(kind="bar", figsize=(10, 6))
plt.title("Evaluation Comparison (Normalized to 0–1 Scale): Direct vs CoT")
plt.ylabel("Normalized Score")
plt.xticks(rotation=20)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("batch_translation/evaluation_comparison_plot_normalized.png")
plt.show()
