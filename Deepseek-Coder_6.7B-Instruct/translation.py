import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re

# === Model Setup (load once) ===
model_id = "deepseek-ai/deepseek-coder-6.7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

# === System prompt ===
system_prompt = """You are a helpful and concise AI programming assistant powered by the Deepseek Coder model, developed by Deepseek Company.

You only answer questions related to computer science, programming, and software engineering. For unrelated or sensitive topics (e.g., politics, security, privacy), you will politely refuse to answer.

You respond to one task at a time. Do not continue with additional examples, tasks, or explanations unless explicitly asked.

You must follow user instructions strictly. If the user asks for code, output only the relevant code and nothing else.

Now begin.

Instruction:
"""

# === translation output extraction ===
def extract_first_python_code(text):
    if "Python Code:" in text:
        text = text.split("Python Code:", 1)[1]
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"(def .+?)(\n\s*\n|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def extract_explanation_only(text):
    if "Explanation:" in text:
        text = text.split("Explanation:", 1)[1].strip()
    return text.strip()

def run(prompt, tokens=512):
    outputs = generator(prompt, max_new_tokens=tokens, do_sample=False)
    return outputs[0]['generated_text']

# === Translation ===
def run_translation(java_path, out_direct_path, out_cot_path):
    with open(java_path, 'r') as f:
        java_code = f.read()

    # Direct Prompt
    prompt_direct = system_prompt + f"""Translate the following Java code to Python. Only output the translated code.

Java Code:
{java_code}"""
    direct_output = run(prompt_direct)
    direct_clean = extract_first_python_code(direct_output)
    with open(out_direct_path, 'w') as f:
        f.write(direct_clean)

    # CoT Step 1
    prompt_explain = system_prompt + f"""Explain what the following Java code does, step by step.

Java Code:
{java_code}"""
    explanation_raw = run(prompt_explain)
    explanation = extract_explanation_only(explanation_raw)

    # CoT Step 2
    prompt_cot = system_prompt + f"""Translate the following Java code to Python using the provided explanation. Only output the translated code.

Explanation:
{explanation}

Java Code:
{java_code}"""
    cot_output = run(prompt_cot)
    cot_clean = extract_first_python_code(cot_output)
    with open(out_cot_path, 'w') as f:
        f.write(cot_clean)
