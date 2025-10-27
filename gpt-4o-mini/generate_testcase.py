import os
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

# === Init OpenAI Client ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
problem_desc_dir = "../codenet_project/problem_descriptions"
output_dir = "test_cases"
os.makedirs(output_dir, exist_ok=True)

def generate(prompt: str, max_completion_tokens=1024) -> str:
    response = client.chat.completions.create(
        model="o4-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that strictly follows input format instructions for programming problems."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=max_completion_tokens  # Required for o4-mini
    )
    return response.choices[0].message.content.strip()


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

    prompt = f"""You are a test case generator for programming problems.

     Your goal is to produce 3 valid test inputs that:
    - **Strictly follow the format of the Sample Input**
    - **Avoid any mathematical expressions** (e.g. use `3 4`, not `3 + 4`)
    - **Only use space-separated numbers, strings, or values as seen in the sample**
    - **Keep each input line raw and directly readable by `input()` or `input().split()`**

     Output Rules:
    - Begin each test case with: `### Test Input 1`, `### Test Input 2`, `### Test Input 3`
    - Include no explanations or outputs
    - Separate each test case with a blank line

    ---

    Input Format:
    {input_section}

    Constraints:
    {constraints_section or 'None'}

    Sample Input:
    {sample_input}

    ---

    Now generate exactly 3 clean test inputs:
    """

    print(f" Generating test inputs for {problem_id} using GPT-4.1-mini...")

    output_text = generate(prompt)
    output_text = output_text.replace("```", "")  # Remove markdown if any

    test_inputs = extract_test_inputs_sequential(output_text)[:3]

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
        print("Usage: python generate_testcase_gpt4mini.py <problem_id>")
    else:
        generate_test_cases(sys.argv[1])
