import os
import re
import csv
import time
from dotenv import load_dotenv
import anthropic
from anthropic._exceptions import OverloadedError

# === Init Claude API ===
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# === Paths ===
batch_dir = "batch_translation/CoT_variant_reflection"
source_java_dir = "../codenet_project/Project_CodeNet_Java250"
output_csv_path = os.path.join("batch_translation", "semantic_accuracy_results_reflection.csv")

# === Prompt builder ===
def build_prompt(java_code, py_code):
    return f"""You are a concise and consistent code evaluation assistant.

Your task is to compare the following two code snippets and judge whether they implement the **same logic**.

 Evaluation Rules:
- Respond using one of the two options: **Yes** or **No**
- Choose **Yes** only if their logic clearly matches
- Choose **No** if unsure or if logic differs

Only return a single word — either **Yes** or **No**.

--- Java Code ---
{java_code}

--- Python Code ---
{py_code}

Do the Java and Python code implement the same logic?
Answer:"""

# === Claude call ===
def generate(prompt: str, max_tokens=64, retries=3, delay=5) -> str:
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=max_tokens,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except OverloadedError:
            print(f" Claude is overloaded. Retrying in {delay}s... ({attempt+1}/{retries})")
            time.sleep(delay)
    return "Overload"

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
        "strategy": "CoT_reflection",
        "semantic_match": result
    })

# === Save results ===
with open(output_csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["problem_id", "submission_id", "strategy", "semantic_match"])
    writer.writeheader()
    writer.writerows(results)

print(f" Semantic evaluation completed using Claude 3.5 Haiku. Results saved to: {output_csv_path}")
