
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import combinations

sns.set(style="whitegrid", context="notebook", font_scale=1.2)

# === Load CSV ===
csv_path = Path("evaluation_summary_all_tidy.csv")
print(f"Loading data from {csv_path} ...")
df = pd.read_csv(csv_path)
print(f" Loaded {len(df)} rows.")
print(df.head())

# === Define Metric Columns ===
metric_cols = ["FunctionalityScore", "SemanticAccuracy", "Readability", "Style"]
print(f" Metrics to plot: {metric_cols}")

#  === PAIRPLOT (all PromptTypes, all Models) ===
print("\n Generating combined pairplot with external legend...")

pairplot = sns.pairplot(
    df,
    vars=metric_cols,
    hue="PromptType",
    palette="tab10",
    corner=False,
    plot_kws={'s': 100, 'edgecolor': 'black', 'linewidth': 0.5},
    diag_kws={'alpha': 0.6}
)

pairplot.fig.suptitle("Pairplot of All Metrics\nColored by PromptType", fontsize=16, y=1.03)
# Move legend outside
pairplot._legend.set_bbox_to_anchor((1.05, 0.5))
pairplot._legend.set_title("PromptType")
plt.tight_layout()

pairplot_file = "pairplot_all_metrics_prompttype.png"
plt.savefig(pairplot_file, dpi=300)
print(f" Saved pairplot to {pairplot_file}")
plt.close()


#  === Regression plots for all metric paris ===
print("\n Generating regression plots for all metric pairs...")
metric_pairs = list(combinations(metric_cols, 2))

for x_metric, y_metric in metric_pairs:
    g = sns.lmplot(
        data=df,
        x=x_metric,
        y=y_metric,
        hue="PromptType",
        palette="tab10",
        markers="o",
        scatter_kws={"s": 80, "edgecolor": "black"},
        height=6,
        aspect=1.2
    )
    plt.title(f"Regression Plot: {x_metric} vs {y_metric}", fontsize=14)
    plt.tight_layout()
    filename = f"regression_{x_metric.lower()}_vs_{y_metric.lower()}.png"
    plt.savefig(filename, dpi=300)
    print(f"   Saved {filename}")
    plt.close()


#  === pari plot per model ===
print("\n Generating separate pairplots for each Model...")

for model in df['Model'].unique():
    print(f"  ➜ Processing Model: {model}")

    model_df = df[df['Model'] == model]

    g = sns.pairplot(
        model_df,
        vars=metric_cols,
        hue="PromptType",
        palette="tab10",
        corner=True,
        plot_kws={'s': 80, 'edgecolor': 'black', 'linewidth': 0.5},
        diag_kws={'alpha': 0.6}
    )

    g.fig.suptitle(f"Pairplot for {model}", fontsize=16, y=1.02)
    plt.tight_layout()

    safe_model = model.lower().replace("-", "_")
    filename = f"pairplot_{safe_model}.png"
    plt.savefig(filename, dpi=300)
    print(f"     Saved {filename}")
    plt.close()



#  === Correlation heatmap (all) ===
print("\n Generating overall correlation heatmap...")

corr = df[metric_cols].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True)
plt.title("Correlation Heatmap of All Metrics", fontsize=14)
plt.tight_layout()

heatmap_file = "correlation_heatmap_overall.png"
plt.savefig(heatmap_file, dpi=300)
print(f" Saved overall heatmap to {heatmap_file}")
plt.close()


#  === Correlation heatmap (prompt type) ===
print("\n Generating correlation heatmaps for each PromptType...")

for prompt in df['PromptType'].unique():
    sub_df = df[df['PromptType'] == prompt]
    corr = sub_df[metric_cols].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True)
    plt.title(f"Correlation Heatmap for {prompt}", fontsize=14)
    plt.tight_layout()

    prompt_safe = prompt.lower().replace(" ", "_").replace("-", "")
    filename = f"heatmap_{prompt_safe}.png"
    plt.savefig(filename, dpi=300)
    print(f"   Saved {filename}")
    plt.close()


print("\n All plots generated successfully!")
