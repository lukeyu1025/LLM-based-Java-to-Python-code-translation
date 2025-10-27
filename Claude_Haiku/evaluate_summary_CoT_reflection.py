
import pandas as pd
import matplotlib.pyplot as plt

# === load evaluation results ===
syn_df = pd.read_csv("batch_translation/syntax_results_reflection.csv")
func_df = pd.read_csv("batch_translation/functionality_results_reflection.csv")
sem_df = pd.read_csv("batch_translation/semantic_accuracy_results_reflection.csv")
read_df = pd.read_csv("batch_translation/readability_results_reflection.csv")
style_df = pd.read_csv("batch_translation/style_pylint_results_reflection.csv")

# === re-label strategy column ===
strategy_label = "CoT-reflection"
syn_df["Strategy"] = strategy_label
sem_df["strategy"] = strategy_label
read_df["Strategy"] = strategy_label
style_df["Strategy"] = strategy_label

# === Syntactic Correctness ===
total_by_strategy = syn_df.groupby("Strategy")["SyntaxPassed"].count()
passed_by_strategy = syn_df[syn_df["SyntaxPassed"] == True].groupby("Strategy")["SyntaxPassed"].count()
syntax_norm = (passed_by_strategy / total_by_strategy).to_dict()

# === Functionality ===
filtered_func_df = func_df[func_df["cot_passed"] >= 0].copy()
filtered_func_df["cot_ratio"] = filtered_func_df["cot_passed"] / filtered_func_df["total"]
func_norm = {strategy_label: filtered_func_df["cot_ratio"].mean()}

# === Semantic accuracy ===
sem_norm = {strategy_label: (sem_df["semantic_match"].str.lower() == "yes").mean()}

# === Readability normalized ===
read_norm = read_df.groupby("Strategy")["MaintainabilityIndex"].mean().div(100).to_dict()

# === Style normalized ===
style_norm = style_df.groupby("Strategy")["PylintScore"].mean().div(10).to_dict()

# === Combine summary results ===
summary_df = pd.DataFrame({
    "Syntactic Correctness": syntax_norm,
    "Functionality Score": func_norm,
    "Semantic Accuracy": sem_norm,
    "Readability (MI)": read_norm,
    "Style (Pylint)": style_norm
}).T

# Save to CSV and plot
summary_csv_path = "batch_translation/evaluation_summary_reflection.csv"
summary_plot_path = "batch_translation/evaluation_summary_plot_reflection.png"
summary_df.to_csv(summary_csv_path)

# Plotting
summary_df.plot(kind="bar", figsize=(10, 6), legend=False)
plt.title("Evaluation (Normalized): CoT Variant - Structured Summary")
plt.ylabel("Normalized Score")
plt.xticks(rotation=20)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig(summary_plot_path)
