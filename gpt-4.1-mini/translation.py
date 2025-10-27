import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# === Init OpenAI API ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === API call ===
def query_gpt41mini(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that translates Java code to Python."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=1024,
    )
    return response.choices[0].message.content

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
- Do NOT use `int(input())` unless it's clearly required for a single-number input.
- Use `input()` or `map(int, input().split())` for space-separated values.
- Avoid type parsing unless the logic depends on numeric comparisons or arithmetic.
- Always ensure outputs are printed using `print(...)`.


Java Code:
{java_code}"""

    direct_output = query_gpt41mini(prompt_direct)
    direct_clean = extract_first_python_code(direct_output).replace("```", "")
    with open(out_direct_path, 'w') as f:
        f.write(direct_clean)

    # === CoT prompt-> step1 generate explanation ===
    prompt_explain = f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""

    explanation_raw = query_gpt41mini(prompt_explain)
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

    cot_output = query_gpt41mini(prompt_cot)
    cot_clean = extract_first_python_code(cot_output).replace("```", "")
    with open(out_cot_path, 'w') as f:
        f.write(cot_clean)

# === CoT Translation Variant ===
def run_CoT_translation_structured_summary(java_path, out_cot_path):
    with open(java_path, 'r') as f:
        java_code = f.read()

    # === CoT prompt-> step1 generate explanation ===
    prompt_explain = f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""
    explanation_raw = query_gpt41mini(prompt_explain)
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
    cot_output = query_gpt41mini(prompt_cot)
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
    explanation_raw = query_gpt41mini(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate pseudocode from explanation ===
    prompt_pseudocode = f"""Convert the following explanation into pseudocode. Keep it clear and structured.

Explanation:
{explanation}"""
    pseudocode = query_gpt41mini(prompt_pseudocode)

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

    cot_output = query_gpt41mini(prompt_translate)
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

    annotated_java = query_gpt41mini(prompt_annotate)

    # === CoT prompt-> step2 generate output with annotated Java ===
    prompt_translate = f"""Translate the following Java code into Python. The Java code includes inline comments explaining each step. Output only the translated Python code (no comments).

 Important Guidelines:
- Do NOT use `int(input())` unless it's clearly required for a single-number input.
- Use `input()` or `map(int, input().split())` for space-separated values.
- Avoid type parsing unless the logic depends on numeric comparisons or arithmetic.
- Always ensure outputs are printed using `print(...)`.

Annotated Java Code:
{annotated_java}"""

    cot_output = query_gpt41mini(prompt_translate)
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
    explanation_raw = query_gpt41mini(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate output with explanation and source Java ===
    prompt_translate = f"""Translate the following Java code into Python using the explanation provided. Output only the translated code.

Explanation:
{explanation}

Java Code:
{java_code}"""
    translation_output = query_gpt41mini(prompt_translate)
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
    reflection_output = query_gpt41mini(prompt_reflect)
    refined_code = extract_first_python_code(reflection_output).replace("```", "").strip()

    # === fallback to first translation if reflection doesn't return new code ===
    if not refined_code or refined_code.lower().startswith("yes"):
        refined_code = translated_code

    with open(out_cot_path, 'w') as f:
        f.write(refined_code)
