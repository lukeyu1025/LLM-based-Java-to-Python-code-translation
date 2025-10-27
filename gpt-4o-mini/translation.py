import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# === Init OpenAI API ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === API call ===
def query_gpt4omini(prompt: str, max_completion_tokens=2048) -> str:
    response = client.chat.completions.create(
        model="o4-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that translates Java code to Python.\n"
                    "\nStrict translation rules (must follow):\n"
                    "- Match input format precisely to how Java reads it.\n"
                    "- Use input() for reading inputs.\n"
                    "  - If Java uses Scanner.nextInt() or next() multiple times on the same line, combine into map(int, input().split()).\n"
                    "  - If each input is on its own line, use separate input() calls.\n"
                    "- Do NOT use int(input()) or similar unless clearly needed for one-value-per-line.\n"
                    "- NEVER assume number of input lines. Match Java input parsing behaviour exactly.\n"
                    "- When parsing arrays or matrices:\n"
                    "  - First read dimensions from input if present.\n"
                    "  - Read 2D arrays row by row using .split() per row.\n"
                    "- Outputs must be printed using print(...) only.\n"
                    "- Do NOT add extra explanation or prompts."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=max_completion_tokens,
    )
    return response.choices[0].message.content.strip()


# === output cleanup ===
def extract_first_python_code(text):
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"(def .+?)(\n\s*\n|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def extract_explanation_only(text):
    if "Explanation:" in text:
        return text.split("Explanation:", 1)[1].strip()
    return text.strip()

# === Translation Pipeline ===
def run_translation(java_path, out_direct_path, out_cot_path):
    with open(java_path, 'r') as f:
        java_code = f.read()

    # === Direct prompt===
    prompt_direct = f"""Translate the following Java code into Python. Output only the translated code.

 Important Guidelines:
- Match input format precisely to how Java reads it.
- Use `input()` for reading inputs.
  - Use `map(int, input().split())` if Java reads multiple values on one line.
  - Use `input()` multiple times if values are read line-by-line.
- Do NOT use `int(input())` unless it's a single-number input on its own line.
- Avoid type parsing unless the logic requires numeric operations.
- When reading matrices, read dimension first then parse row-by-row.
- Always use `print(...)` for output.

Java Code:
{java_code}"""

    direct_output = query_gpt4omini(prompt_direct)
    direct_clean = extract_first_python_code(direct_output).replace("```", "")
    with open(out_direct_path, 'w') as f:
        f.write(direct_clean)

    # === CoT prompt-> step1 generate explanation ===
    prompt_explain = f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""

    explanation_raw = query_gpt4omini(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate output with explanation and source Java ===
    prompt_cot = f"""Translate the following Java code into Python using the explanation provided. Output only the translated code.

 Important Guidelines:
- Match input format precisely to how Java reads it.
- Use `input()` or `map(int, input().split())` appropriately based on how Java reads input.
- Do NOT use `int(input())` unless clearly required for single-number inputs.
- Parse matrices based on declared size and input format.
- Always ensure output is printed with `print(...)`.

Explanation:
{explanation}

Java Code:
{java_code}"""

    cot_output = query_gpt4omini(prompt_cot)
    cot_clean = extract_first_python_code(cot_output).replace("```", "")
    with open(out_cot_path, 'w') as f:
        f.write(cot_clean)

# [Other CoT variants remain unchanged]
def run_CoT_translation_structured_summary(java_path, out_cot_path):
    with open(java_path, 'r') as f:
        java_code = f.read()

    # === CoT prompt-> step1 generate explanation ===
    prompt_explain = f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""
    explanation_raw = query_gpt4omini(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate output with explanation and source Java ===
    prompt_cot = f"""Translate the following Java code into Python using the explanation provided. Output only the translated code.

 Important Guidelines:
- Do NOT use `int(input())` unless it's clearly required for a single-number input.
- Use `input()` or `map(int, input().split())` for space-separated values.
- Avoid type parsing unless the logic depends on numeric comparisons or arithmetic.
- Always ensure outputs are printed using `print(...)`.

Explanation:
{explanation}

Java Code:
{java_code}"""
    cot_output = query_gpt4omini(prompt_cot)
    cot_clean = extract_first_python_code(cot_output).replace("```", "")
    with open(out_cot_path, 'w') as f:
        f.write(cot_clean)

def run_CoT_translation_pseudocode(java_path, out_cot_path):
    with open(java_path, 'r') as f:
        java_code = f.read()

    # === CoT prompt-> step1 generate explanation ===
    prompt_explain = f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""
    explanation_raw = query_gpt4omini(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate pseudocode from explanation ===
    prompt_pseudocode = f"""Convert the following explanation into pseudocode. Keep it clear and structured.

Explanation:
{explanation}"""
    pseudocode = query_gpt4omini(prompt_pseudocode)

    # === CoT prompt-> step3 generate output with pseudocode and source Java ===
    prompt_translate = f"""Translate the following Java code into Python using the provided pseudocode as a guide. Output only the translated code.

 Important Guidelines:
- Do NOT use `int(input())` unless it's clearly required for a single-number input.
- Use `input()` or `map(int, input().split())` for space-separated values.
- Avoid type parsing unless the logic depends on numeric comparisons or arithmetic.
- Always ensure outputs are printed using `print(...)`.

--- Java Code ---
{java_code}

--- Pseudocode ---
{pseudocode}"""

    cot_output = query_gpt4omini(prompt_translate)
    cot_clean = extract_first_python_code(cot_output).replace("```", "")
    with open(out_cot_path, 'w') as f:
        f.write(cot_clean)

def run_CoT_translation_annotated_code(java_path, out_cot_path):
    with open(java_path, 'r') as f:
        java_code = f.read()

    # === CoT prompt-> step1 generate annotated Java code ===
    prompt_annotate = f"""Add helpful inline comments to explain the purpose of each line or block in the following Java code. Use '// ...' style comments.

Java Code:
{java_code}"""

    annotated_java = query_gpt4omini(prompt_annotate)

    # === CoT prompt-> step2 generate output with annotated Java ===
    prompt_translate = f"""Translate the following Java code into Python. The Java code includes inline comments explaining each step. Output only the translated Python code (no comments).

 Important Guidelines:
- Do NOT use `int(input())` unless it's clearly required for a single-number input.
- Use `input()` or `map(int, input().split())` for space-separated values.
- Avoid type parsing unless the logic depends on numeric comparisons or arithmetic.
- Always ensure outputs are printed using `print(...)`.

Annotated Java Code:
{annotated_java}"""

    cot_output = query_gpt4omini(prompt_translate)
    cot_clean = extract_first_python_code(cot_output).replace("```", "")
    with open(out_cot_path, 'w') as f:
        f.write(cot_clean)


def run_CoT_translation_reflection(java_path, out_cot_path):
    with open(java_path, 'r') as f:
        java_code = f.read()

    # === CoT prompt-> step1 generate explanation ===
    prompt_explain = f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""
    explanation_raw = query_gpt4omini(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate output with explanation and source Java ===
    prompt_translate = f"""Translate the following Java code into Python using the explanation provided. Output only the translated code.

Explanation:
{explanation}

Java Code:
{java_code}"""
    translation_output = query_gpt4omini(prompt_translate)
    translated_code = extract_first_python_code(translation_output).replace("```", "").strip()

    # === CoT prompt-> step3 reflction from translated output ===
    prompt_reflect = f"""You are reviewing the following Python code translated from Java. 
If there are any logical mistakes or missing parts, fix them. Otherwise, confirm the code is correct.

Original Java:
{java_code}

Explanation:
{explanation}

Translated Python:
{translated_code}

Now provide the corrected Python code if needed. Output only the corrected code block."""
    reflection_output = query_gpt4omini(prompt_reflect)
    refined_code = extract_first_python_code(reflection_output).replace("```", "").strip()

    # === fallback to first translation if reflection doesn't return new code ===
    if not refined_code or refined_code.lower().startswith("yes"):
        refined_code = translated_code

    with open(out_cot_path, 'w') as f:
        f.write(refined_code)
