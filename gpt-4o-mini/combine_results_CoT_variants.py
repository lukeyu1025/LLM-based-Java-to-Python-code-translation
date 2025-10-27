import os
import pandas as pd
import matplotlib.pyplot as plt

# === Source paths ===
main_summary = "batch_translation/evaluation_summary.csv"
variant_files = {
    "CoT-StructuredSummary": "batch_translation/evaluation_summary_structured_summary.csv",
    "CoT-pseudocode": "batch_translation/evaluation_summary_pseudocode.csv",
    "CoT-annotated": "batch_translation/evaluation_summary_annotated.csv",
    "CoT-reflection": "batch_translation/evaluation_summary_reflection.csv",
}

# === load column from Dir vs CoT summary ===
if not os.path.exists(main_summary):
    raise FileNotFoundError(f"Main summary not found: {main_summary}")

main_df = pd.read_csv(main_summary, index_col=0)
cot_column = main_df[["CoT"]].rename(columns={"CoT": "CoT"})

# === Load CoT variant summary ===
all_dfs = [cot_column]
for label, path in variant_files.items():
    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0)
        df.columns = [label]
        all_dfs.append(df)
    else:
        print(f" Missing file: {path}")

# === Merge all dataframes ===
merged_df = pd.concat(all_dfs, axis=1)

# === Save merged result ===
merged_csv = "batch_translation/evaluation_summary_combined.csv"
merged_df.to_csv(merged_csv)
print(f" Combined summary saved to {merged_csv}")

# === Plotting ===
merged_df.plot(kind="bar", figsize=(12, 6))
plt.title("Comparison of CoT Prompting Variants (Normalized Metrics)")
plt.ylabel("Normalized Score")
plt.xticks(rotation=20)
plt.grid(axis="y")
plt.tight_layout()
plot_path = "batch_translation/evaluation_summary_combined_plot.png"
plt.savefig(plot_path)
print(f" Plot saved to {plot_path}")
