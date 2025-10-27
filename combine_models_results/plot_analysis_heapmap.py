
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

sns.set(style="whitegrid", context="notebook", font_scale=1.2)

# === Load CSV ===
csv_path = Path("evaluation_summary_all_tidy.csv")
print(f"Loading data from {csv_path} ...")
df = pd.read_csv(csv_path)
print(f" Loaded {len(df)} rows.")

metric_cols = ["FunctionalityScore", "SemanticAccuracy", "Readability", "Style"]

# === Define groups ===
high_correlation_variants = ['CoT-reflection', 'CoT-annotated']
low_correlation_variants = ['CoT-pseudocode', 'CoT-StructuredSummary']

# === Setup figure ===
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
axes = axes.flatten()

# === plot highest correlation pair ===
for i, variant in enumerate(high_correlation_variants):
    sub_df = df[df['PromptType'] == variant]
    corr = sub_df[metric_cols].corr()
    sns.heatmap(
        corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, square=True,
        ax=axes[i]
    )
    axes[i].set_title(f"{variant.replace('CoT-', '').capitalize()}")

# === plot lowest correlation pair ===
for i, variant in enumerate(low_correlation_variants, start=2):
    sub_df = df[df['PromptType'] == variant]
    corr = sub_df[metric_cols].corr()
    sns.heatmap(
        corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, square=True,
        ax=axes[i]
    )
    axes[i].set_title(f"{variant.replace('CoT-', '').capitalize()}")

# === plot layout ===
fig.suptitle(
    "Correlation Heatmaps for CoT Variants\nHigh-correlation (Left) vs Low-correlation (Right)",
    fontsize=16
)
plt.tight_layout(rect=[0, 0, 1, 0.95])

# === Save ===
output_file = "heatmaps_contrast_high_vs_low.png"
plt.savefig(output_file, dpi=300)
print(f"\n Saved contrast heatmap figure to {output_file}")

plt.show()
