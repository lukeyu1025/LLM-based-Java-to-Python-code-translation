import os
import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# Paths
problem_desc_dir = "../codenet_project/problem_descriptions"
output_dir = "test_cases"
os.makedirs(output_dir, exist_ok=True)

# Load model
model_id = "deepseek-ai/deepseek-coder-6.7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def extract_section(soup, label):
    headings = soup.find_all(re.compile("^h[1-6]$"))
    for h in headings:
        if label.lower() in h.get_text(strip=True).lower():
            pre = h.find_next_sibling("pre")
            if pre:
                return pre.get_text(strip=True)
            content = []
            for sib in h.find_next_siblings():
                if sib.name and re.match(r"h[1-6]", sib.name, re.IGNORECASE):
                    break
                content.append(sib.get_text(strip=True))
            return "\n".join(content).strip()
    return None


def extract_test_inputs_sequential(text):
    inputs = []
    blocks = text.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().splitlines()
        if lines and lines[0].startswith("### Test Input"):
            inputs.append("\n".join(lines[1:]).strip())
    return inputs


def generate_test_cases(problem_id):
    html_path = os.path.join(problem_desc_dir, f"{problem_id}.html")
    if not os.path.exists(html_path):
        print(f" Description not found for {problem_id}")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    input_section = extract_section(soup, "Input")
    constraints_section = extract_section(soup, "Constraints")
    sample_input = extract_section(soup, "Sample Input")

    if not input_section or not sample_input:
        print(f" Missing input or sample input for {problem_id}, skipping.")
        return

    # Prompt
    prompt = f"""You are a helpful assistant.

    Your task is to generate exactly 3 valid test inputs for a coding problem. Follow the sample input format **exactly**.

     Rules:
    - Use the **same input format** as the Sample Input.
    - Do **NOT** add variable names or assignments (e.g., `R = 50` is invalid if the sample input is just `50`).
    - Only output 3 test inputs.
    - Start each test input with: ### Test Input 1, ### Test Input 2, ### Test Input 3
    - Do **NOT** include explanation, output, or code formatting.
    - Separate each test input with a blank line.

    ---

    Input Format:
    {input_section}

    Constraints:
    {constraints_section or 'None'}

    Sample Input:
    {sample_input}

    ---

    Now generate 3 new test inputs that match the exact format of the Sample Input:
    """

    print(f" Generating test inputs for {problem_id}...")
    result = generator(prompt, max_new_tokens=512, do_sample=False)
    output_text = result[0]["generated_text"]

    # Extract only the test inputs from the output
    # Extract only the first 3 test inputs from the output
    test_inputs = extract_test_inputs_sequential(output_text)[:3]

    # Save cleaned result
    out_path = os.path.join(output_dir, f"{problem_id}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Sample Input:\n")
        f.write(sample_input.strip() + "\n\n")
        for i, ti in enumerate(test_inputs, start=1):
            f.write(f"### Test Input {i}\n{ti.strip()}\n\n")

    print(f" Clean test inputs saved to {out_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python generate_testcase.py <problem_id>")
    else:
        generate_test_cases(sys.argv[1])
