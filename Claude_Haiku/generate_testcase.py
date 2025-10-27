import os
import re
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import anthropic
from anthropic._exceptions import OverloadedError

# === Init Claude Client ===
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# === Paths ===
problem_desc_dir = "../codenet_project/problem_descriptions"
output_dir = "test_cases"
os.makedirs(output_dir, exist_ok=True)

# === Claude LLM call with retry ===
def generate(prompt: str, max_tokens=1024, retries=3, delay=5) -> str:
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except OverloadedError:
            print(f" Claude is overloaded. Retrying in {delay} seconds... ({attempt + 1}/{retries})")
            time.sleep(delay)
    return "[ERROR: Claude overload]"

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

    # === Check if space-separated input appears in sample ===
    space_separated = any(" " in line for line in sample_input.strip().splitlines())
    format_note = (
        "-  Use one input per line (no space-separated values)"
        if not space_separated else
        "-  You may use space-separated values if it matches the sample"
    )
    print(f" Detected input format for {problem_id}: {'space-separated' if space_separated else 'line-by-line'}")

    # === Build prompt dynamically based on input style ===
    prompt = f"""You are a test case generator for programming problems.

 Your goal is to produce 3 valid test inputs that:
- **Strictly follow the format of the Sample Input**
- **Avoid any mathematical expressions** (e.g. use `3 4`, not `3 + 4`)
- **Only use numeric or string values in formats shown in the sample**
{format_note}
- **Each line must be directly readable by `input()` or `input().split()`**

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

    print(f" Generating test inputs for {problem_id} using Claude 4 Sonnet...")

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

# === CLI Entrypoint ===
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python generate_testcase.py <problem_id>")
    else:
        generate_test_cases(sys.argv[1])
