import os
import re
import csv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# === Paths ===
batch_dir = "batch_translation"
source_java_dir = "../codenet_project/Project_CodeNet_Java250"
output_csv_path = os.path.join(batch_dir, "semantic_accuracy_results.csv")

# === Load Gemma 7B (instruction-tuned) ===
model_id = "google/gemma-7b-it"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

def generate(prompt: str, max_new_tokens=128) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# === Prompt builder ===
def build_prompt(java_code, py_code):
    return f"""You are a strict and concise code evaluation assistant.

You are given two code snippets. Determine whether they implement the **same logic**.

 Rules:
- ONLY respond with **"Yes"** or **"No"**
- Do **NOT** explain your answer.
- Do **NOT** output anything else.
- If unsure, choose **"No"**

--- Java Code ---
{java_code}

--- Python Code ---
{py_code}

Do the Java and Python code implement the same logic?
Answer:"""

# === semantic accuracy evaluation function ===
def evaluate_semantic(problem_id, submission_id, path_py):
    java_path = os.path.join(source_java_dir, problem_id, f"{submission_id}.java")
    if not os.path.exists(java_path):
        return "Missing Java"

    try:
        with open(java_path, "r", encoding="utf-8") as f:
            java_code = f.read()
        with open(path_py, "r", encoding="utf-8") as f:
            py_code = f.read()
    except Exception:
        return "Load Error"

    prompt = build_prompt(java_code, py_code)
    output_text = generate(prompt)

    match = re.search(r"\b(Yes|No)\b", output_text, re.IGNORECASE)
    return match.group(1).capitalize() if match else "Unknown"

# === evaluate Dir and CoT translation ===
results = []
for strategy in ["direct", "CoT"]:
    strategy_dir = os.path.join(batch_dir, strategy)
    for fname in os.listdir(strategy_dir):
        if not fname.endswith(".py"):
            continue
        parts = fname.split("_")
        if len(parts) != 3:
            continue
        problem_id, submission_id, _ = parts
        file_path = os.path.join(strategy_dir, fname)
        result = evaluate_semantic(problem_id, submission_id, file_path)
        results.append({
            "problem_id": problem_id,
            "submission_id": submission_id,
            "strategy": strategy,
            "semantic_match": result
        })

# === Save results ===
with open(output_csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["problem_id", "submission_id", "strategy", "semantic_match"])
    writer.writeheader()
    writer.writerows(results)

print(f" Semantic evaluation completed using Gemma. Results saved to: {output_csv_path}")
