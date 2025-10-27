import os
import re
from dotenv import load_dotenv
import anthropic
import time
from anthropic._exceptions import OverloadedError


GUIDELINES = """
You are a helpful assistant that translates Java code to Python.

Follow these input handling instructions:

- When the Java code reads multiple values from the same line (e.g., `sc.nextInt()` used twice on the same line), use `input().split()` and unpack the variables, e.g., `a, b = input().split()`.

- When the Java code reads one value per line (e.g., `sc.nextInt()` on separate lines), use separate `input()` calls for each value, e.g., `a = input(); b = input();`.

- If the Java code uses `nextLine().split()` or chained `nextInt()` on a line, prefer `input().split()` and unpack the values.

- Convert input to integers or floats only when necessary for mathematical operations, using `map()` if needed (e.g., `map(int, input().split())`).

Output only valid Python code. No Markdown formatting. No explanation.

"""


# === Load API Key and Create Claude Client ===
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def query_claude(prompt, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                system=GUIDELINES,
                max_tokens=1024,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
        except OverloadedError:
            print(f" Claude is overloaded. Retrying in {delay} seconds... (attempt {attempt + 1}/{retries})")
            time.sleep(delay)
        except Exception as e:
            print(f" Unexpected error during Claude call: {e}")
            break
    return "[ERROR: Claude did not respond]"

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

    prompt_direct = f"""Translate the following Java code into Python. Output only the translated code.

Java Code:
{java_code}"""
    direct_output = query_claude(prompt_direct)
    direct_clean = extract_first_python_code(direct_output).replace("```", "")
    with open(out_direct_path, 'w') as f:
        f.write(direct_clean)

    prompt_explain = f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""
    explanation_raw = query_claude(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    prompt_cot = f"""Translate the following Java code into Python using the explanation provided. Output only the translated code.

Explanation:
{explanation}

Java Code:
{java_code}"""
    cot_output = query_claude(prompt_cot)
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
    explanation_raw = query_claude(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate output with explanation and source Java ===
    prompt_cot = f"""Translate the following Java code into Python using the explanation provided. Output only the translated code.

Explanation:
{explanation}

Java Code:
{java_code}"""
    cot_output = query_claude(prompt_cot)
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
    explanation_raw = query_claude(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate pseudocode from explanation ===
    prompt_pseudocode = f"""Convert the following explanation into pseudocode. Keep it clear and structured.

Explanation:
{explanation}"""
    pseudocode = query_claude(prompt_pseudocode)

    # === CoT prompt-> step3 generate output with pseudocode and source Java ===
    prompt_translate = f"""Translate the following Java code into Python using the provided pseudocode as a guide. Output only the translated code.

--- Java Code ---
{java_code}

--- Pseudocode ---
{pseudocode}"""

    cot_output = query_claude(prompt_translate)
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

    annotated_java = query_claude(prompt_annotate)

    # === CoT prompt-> step2 generate output with annotated Java ===
    prompt_translate = f"""Translate the following Java code into Python. The Java code includes inline comments explaining each step. Output only the translated Python code (no comments).

Annotated Java Code:
{annotated_java}"""

    cot_output = query_claude(prompt_translate)
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
    explanation_raw = query_claude(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # === CoT prompt-> step2 generate output with explanation and source Java ===
    prompt_translate = f"""Translate the following Java code into Python using the explanation provided. Output only the translated code.

Explanation:
{explanation}

Java Code:
{java_code}"""
    translation_output = query_claude(prompt_translate)
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
    reflection_output = query_claude(prompt_reflect)
    refined_code = extract_first_python_code(reflection_output).replace("```", "").strip()

    # === fallback to first translation if reflection doesn't return new code ===
    if not refined_code or refined_code.lower().startswith("yes"):
        refined_code = translated_code

    with open(out_cot_path, 'w') as f:
        f.write(refined_code)
