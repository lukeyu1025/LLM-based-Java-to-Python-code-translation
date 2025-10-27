import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import re

# === Model Setup ===
model_id = "google/gemma-7b-it"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

def generate(prompt, max_new_tokens=512):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# === translation output extraction ===
def extract_first_python_code(text):
    # Case 1: Fenced code block
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Case 2: Indented block following "Python Code:"
    if "Python Code:" in text:
        code_part = text.split("Python Code:", 1)[1]
        # Remove "**Output:**" or anything after another markdown section
        code_part = re.split(r"\*\*.*?\*\*", code_part)[0]
        # Remove markdown-style emphasis
        code_part = re.sub(r"\*\*", "", code_part)
        return code_part.strip()

    # Case 3: Fallback to finding first function or import block
    match = re.search(r"(import .+?)(\n\s*\n|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"(def .+?)(\n\s*\n|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Final cleanup
    return text.strip()

def extract_explanation_only(text):
    if "Explanation:" in text:
        return text.split("Explanation:", 1)[1].strip()
    return text.strip()

# === Translation ===
def run_translation(java_path, out_direct_path, out_cot_path):
    with open(java_path, 'r') as f:
        java_code = f.read()

    # Direct Prompt
    prompt_direct = f"""Translate the following Java code into Python. Output only the translated code.

Java Code:
{java_code}"""
    direct_output = generate(prompt_direct)
    direct_clean = extract_first_python_code(direct_output)
    direct_clean = direct_clean.replace("```", "")
    with open(out_direct_path, 'w') as f:
        f.write(direct_clean)

    #  === CoT prompt-> step1 generate explanation ===
    prompt_explain = f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""
    explanation_raw = generate(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    #  === CoT prompt-> step2 generate output with explanation and source Java ===
    prompt_cot = f"""Translate the following Java code to Python using the provided explanation. Output only the translated code.

Explanation:
{explanation}

Java Code:
{java_code}"""
    cot_output = generate(prompt_cot)
    cot_clean = extract_first_python_code(cot_output)
    cot_clean = cot_clean.replace("```", "")
    with open(out_cot_path, 'w') as f:
        f.write(cot_clean)
