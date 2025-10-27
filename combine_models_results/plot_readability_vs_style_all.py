
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# === Seaborn settings ===
sns.set(style="whitegrid", context="notebook", font_scale=1.2)

# === Load data ===
csv_path = Path("evaluation_summary_all_tidy.csv")
print(f"Loading data from {csv_path} ...")
df = pd.read_csv(csv_path)
print(f" Loaded {len(df)} rows.")

# === Define plot ===
print(" Plotting Readability vs Style...")

plt.figure(figsize=(9, 7))
scatter = sns.scatterplot(
    data=df,
    x="Readability",
    y="Style",
    hue="PromptType",
    style="Model",
    s=120,
    palette="tab10",
    edgecolor="black",
    linewidth=0.5
)

# === draw regression line ===
sns.regplot(
    data=df,
    x="Readability",
    y="Style",
    scatter=False,
    color='gray',
    line_kws={'label':"Overall Trend"},
    ci=95
)

# === Title and labels ===
plt.title("Readability vs Style across all Models and Prompting Strategies", fontsize=14)
plt.xlabel("Readability (MI Score)", fontsize=12)
plt.ylabel("Style (Pylint Score)", fontsize=12)

# === Legend ===
plt.legend(title="PromptType / Model", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# === Save figure ===
output_file = "readability_vs_style_all_prompttypes_models.png"
plt.savefig(output_file, dpi=300)
print(f"\n Saved scatter plot to {output_file}")

plt.show()
