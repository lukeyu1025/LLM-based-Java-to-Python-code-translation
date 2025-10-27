import os
import re
import csv
from dotenv import load_dotenv
from openai import OpenAI

# === Init OpenAI API ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Paths ===
batch_dir = "batch_translation/CoT_variant_annotated"
source_java_dir = "../codenet_project/Project_CodeNet_Java250"
output_csv_path = os.path.join("batch_translation", "semantic_accuracy_results_annotated.csv")

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

# === LLM call ===
def generate(prompt: str, max_completion_tokens=64) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict and concise code evaluation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=1,  # gpt-4o-mini only supports default temperature
        max_completion_tokens=max_completion_tokens,
    )

    result = response.choices[0].message.content.strip()
    finish_reason = response.choices[0].finish_reason
    if finish_reason != "stop":
        print(f" Warning: Incomplete generation (finish_reason = {finish_reason})")
    return result

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

# === evaluate CoT variant ===
results = []
for fname in os.listdir(batch_dir):
    if not fname.endswith(".py"):
        continue
    parts = fname.split("_")
    if len(parts) < 3:
        continue
    problem_id = parts[0]
    submission_id = parts[1]
    file_path = os.path.join(batch_dir, fname)
    result = evaluate_semantic(problem_id, submission_id, file_path)
    results.append({
        "problem_id": problem_id,
        "submission_id": submission_id,
        "strategy": "CoT_annotated",
        "semantic_match": result
    })

# === Save results ===
with open(output_csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["problem_id", "submission_id", "strategy", "semantic_match"])
    writer.writeheader()
    writer.writerows(results)

print(f" Semantic evaluation completed using GPT-4.1-mini for CoT structured summary. Results saved to: {output_csv_path}")
