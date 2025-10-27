import pandas as pd
import matplotlib.pyplot as plt
import os

# === File path ===
file_path = "evaluation_summary_all_tidy_manual.csv"

# === Load data ===
df = pd.read_csv(file_path)

# Filter only Direct and CoT
df_filtered = df[df['PromptType'].isin(['Direct', 'CoT'])]

# Metrics to generate charts for
metrics = {
    'SyntacticCorrectness': 'Syntax',
    'FunctionalityScore': 'Functionality',
    'SemanticAccuracy': 'Semantic Accuracy',
    'Readability': 'Readability',
    'Style': 'Style'
}

# Output folder
output_folder = "figures_pos_neg_manual"
os.makedirs(output_folder, exist_ok=True)

print("Generating charts for models:", df['Model'].unique())

# === Generate positive-negative bar charts ===
for col, metric_name in metrics.items():
    # Pivot to calculate CoT - Direct difference for each model
    df_diff = df_filtered.pivot_table(index='Model', columns='PromptType', values=col, aggfunc='mean')
    df_diff['Difference'] = df_diff['CoT'] - df_diff['Direct']

    # Sort for better visualization
    df_diff = df_diff.sort_values(by='Difference', ascending=False)

    # Colors: orange for positive improvement, green for worse performance
    colors = ['orange' if x > 0 else 'green' for x in df_diff['Difference']]

    # Plot
    plt.figure(figsize=(8, 5))
    plt.bar(df_diff.index, df_diff['Difference'], color=colors)
    plt.axhline(0, color='black', linewidth=1)
    plt.title(f'CoT Improvement over Direct - {metric_name}')
    plt.ylabel('Difference (CoT - Direct)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save figure
    output_path = os.path.join(output_folder, f'{metric_name.lower().replace(" ", "_")}_diff_pos_neg.png')
    plt.savefig(output_path, dpi=300)
    plt.close()

print(f"✅ Positive-negative bar charts generated and saved in '{output_folder}'")
