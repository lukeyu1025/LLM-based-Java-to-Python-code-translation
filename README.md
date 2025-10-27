This archive contains all scripts developed for this project, including the translation process, evaluation pipeline, and analysis process.

---

# 1. Environment Setup
Install all required Python packages:

```bash
pip install -r requirements.txt
```

---

# 2. API Key Setup
For API based models(gpt-4.1-mini, gpt-4o-mini, Claude_Haiku, Claude_Sonnet)

Create `.env` file and placed in each model folder
## `.env` file format:

ANTHROPIC_API_KEY=your_anthropic_api_key_here

OPENAI_API_KEY=your_openai_api_key_here

# 3. Dataset Preparation

- Download the dataset from [Project_CodeNet_Java250.tar.gz](https://dax-cdn.cdn.appdomain.cloud/dax-project-codenet/1.0.0/Project_CodeNet_Java250.tar.gz)
- Ensure Project CodeNet Java source is placed at ``\codenet_project\Project_CodeNet_Java250``
- Place it in the project directory before running translation scripts.

---

# 4. Directory Structure

### For API-Based Models(gpt-4.1-mini, gpt-4o-mini, Claude_Haiku, Claude_Sonnet)

Running the translation script **once** generates outputs for all prompt types and CoT variants in the `batch_translation` subfolder:

- `Direct`
- `CoT`
- `CoT_variant_annotated`
- `CoT_variant_pseudocode`
- `CoT_variant_reflection`
- `CoT_variant_structured_summary`

> **Note:**  
> - **The translation scripts generate all variants in one script**  
> - **Evaluation scripts must be run separately for each variant.**

### For Local Models(Deepseek-Coder_6.7B-Instruct,CodeGemma)

Local models only translate the two basic prompt strategies:

- `Direct`
- `CoT`

---

# 5. Usage Order

Below is the **step-by-step order** for using these scripts.

### 1️. Translation Step (batch translation for all strategies)
```
python batch_translate.py
```
- Generates translations for:
	- Direct
	- Basic CoT
	- All CoT variants
- Each is saved in its subfolder under `batch_translation`.

### 2️. Evaluation and Analysis Step(Direct and Basic CoT)
```
python evaluate_syntax.py
python evaluate_functionality.py
python evaluate_semantic.py
python evaluate_readability.py
python evaluate_style.py
```
- Functionality evaluation will look up test cases in the `test_cases` subfolder and run `generate_testcase.py` if missing.

- Evaluation results are saved in `batch_translation` as:
```
syntax_results.csv
functionality_results.csv
semantic_accuracy_results.csv
readability_results.csv
style_pylint_results.csv
```

- Combine evaluation results:
```
python evaluate_summary.py
```

- Analysis results saved as:
```
evaluation_comparison_plot_normalized.png
evaluation_summary.csv
```

### 3️. Evaluation and Analysis Step( for CoT variants)
- Run separately for each CoT variant:
```
python evaluate_syntax_[variants].py
python evaluate_functionality_[variants].py
python evaluate_semantic_[variants].py
python evaluate_readability_[variants].py
python evaluate_style_[variants].py
```

- Evaluation results are saved as:
```
syntax_results_[variants].csv
functionality_results_[variants].csv
semantic_accuracy_results_[variants].csv
readability_results_[variants].csv
style_pylint_results_[variants].csv
```

- Combine evaluation results:
```
python evaluate_summary_[CoT variants].py
```

- Analysis results are saved in the subfolder `batch_translation` as
```
evaluation_comparison_plot_normalized_[CoT variants].png
evaluation_summary_[CoT variants].csv
```

### 4️. Results Combination:
```
python combine_results_CoT_variants.py
```
- Merges all evaluation summary for cross-strategy comparison.
- Outputs:
```
evaluation_summary_combined_plot.png
evaluation_summary_combined.csv
```

> **Note:** 
> - For Local Models (Deepseek-Coder, CodeGemma), no CoT variants or combination step is needed.

---

# 6. Script Descriptions

- `batch_translate.py`: 
	Randomly selects a batch of valid Java source code and calls `run_translation(java_path, out_direct, out_cot)` in `translation.py`.

- `translation.py`:
	Generates translation from Java source code saved in subfolders.

- `evaluate_syntax.py`:
	Evaluates the syntactic correctness of translated code

- evaluate_functionality.py:
	Test functionality using test cases. Runs `generate_testcase.py` if test cases are missing.

- `generate_testcase.py`:
	Generates test inputs based on problem descriptions in the dataset metadata.

- `evaluate_semantic.py`:
	Compares Java and translates Python code using LLM-based semantic judgment.

- `evaluate_readability.py`:
	Uses the `radon` library to calculate the `Maintainability Index`.

- `evaluate_style.py`:
	Uses `pylint` to rate code style according to PEP8.

- `evaluate_summary.py`
	Combines all evaluation results to compare direct and Basic CoT prompts.
	> Note: for CoT variants, `evaluate_summary.py` only combines results for that variant.

- `combine_results_CoT_variants.py`:
	Combines all variant summary and Basis CoT summary for cross-strategy analysis.
