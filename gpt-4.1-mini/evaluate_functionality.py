import os
import re
import subprocess
import csv
from typing import List, Tuple
import ast


batch_dir = "batch_translation"
source_java_dir = "../codenet_project/Project_CodeNet_Java250"
testcase_dir = "test_cases"
generate_script = "generate_testcase.py"

def check_syntax(file_path: str) -> bool:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def run_python_with_input(code_path: str, input_data: str) -> Tuple[str, str]:
    try:
        result = subprocess.run(
            ["python3", code_path],
            input=input_data.encode("utf-8"),
            capture_output=True,
            timeout=5
        )
        return result.stdout.decode("utf-8").strip(), result.stderr.decode("utf-8")
    except subprocess.TimeoutExpired:
        return "", "Timeout"

def run_java_with_input(java_path: str, input_data: str) -> Tuple[str, str]:
    java_dir = os.path.dirname(java_path)
    main_path = os.path.join(java_dir, "Main.java")

    try:
        # Copy contents to Main.java
        with open(java_path, "r", encoding="utf-8") as original:
            code = original.read()
        with open(main_path, "w", encoding="utf-8") as temp:
            temp.write(code)

        # Compile Main.java
        compile = subprocess.run(["javac", "Main.java"], cwd=java_dir, capture_output=True)
        if compile.returncode != 0:
            return "", compile.stderr.decode("utf-8")

        # Run Main
        result = subprocess.run(
            ["java", "Main"],
            input=input_data.encode("utf-8"),
            capture_output=True,
            cwd=java_dir,
            timeout=5
        )
        return result.stdout.decode("utf-8").strip(), result.stderr.decode("utf-8")

    except subprocess.TimeoutExpired:
        return "", "Timeout"
    finally:
        # Clean up temporary Main.java and .class
        if os.path.exists(main_path):
            os.remove(main_path)
        class_file = os.path.join(java_dir, "Main.class")
        if os.path.exists(class_file):
            os.remove(class_file)

def parse_test_inputs(filepath: str) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    inputs = []

    # Extract Sample Input
    sample_match = re.search(r"Sample Input:\s*\n(.*?)(?=\n### Test Input 1|\Z)", content, re.DOTALL)
    if sample_match:
        sample_input = sample_match.group(1).strip()
        inputs.append(sample_input)

    # Extract exactly the first 3 unique test inputs
    seen = set()
    for i in range(1, 4):
        pattern = rf"### Test Input {i}\s*\n(.*?)(?=\n### Test Input \d|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
            if cleaned not in seen:
                inputs.append(cleaned)
                seen.add(cleaned)

    return inputs

def evaluate(filename: str, path_direct: str, path_cot: str) -> dict:
    problem_id = filename.split("_")[0]
    submission_id = filename.split("_")[1]
    java_path = os.path.join(source_java_dir, problem_id, f"{submission_id}.java")
    tc_path = os.path.join(testcase_dir, f"{problem_id}.txt")

    if not os.path.exists(tc_path):
        print(f" Test case not found for {filename}. Generating...")
        subprocess.run(["python3", generate_script, problem_id])

    if not os.path.exists(tc_path):
        print(f" Still missing test case for {filename}")
        return None

    test_inputs = parse_test_inputs(tc_path)
    result = {
        "problem_id": problem_id,
        "direct_passed": 0,
        "cot_passed": 0,
        "total": 0  
    }

    print(f"\nEvaluating problem {problem_id}...")

    for i, inp in enumerate(test_inputs, start=1):
        print(f"\n--- Test Input {i} ---\n{inp}")

        expected, java_err = run_java_with_input(java_path, inp)
        if java_err or not expected.strip():
            print(f"Java Error (skipping test case):\n{java_err.strip()}")
            continue  

        print(f"Java Output:\n{expected}")
        result["total"] += 1

        if os.path.exists(path_direct) and check_syntax(path_direct):
            out, err = run_python_with_input(path_direct, inp)
            print(f"Direct Output:\n{out if not err else err}")
            if out == expected and not err:
                result["direct_passed"] += 1
        else:
            print("Direct code has syntax error. Skipping.")
            result["direct_passed"] = -99

        if os.path.exists(path_cot) and check_syntax(path_cot):
            out, err = run_python_with_input(path_cot, inp)
            print(f"CoT Output:\n{out if not err else err}")
            if out == expected and not err:
                result["cot_passed"] += 1
        else:
            print("CoT code has syntax error. Skipping.")
            result["cot_passed"] = -99

    return result

def evaluate_all():
    results = []
    direct_dir = os.path.join(batch_dir, "direct")
    cot_dir = os.path.join(batch_dir, "CoT")

    for fname in os.listdir(direct_dir):
        if not fname.endswith("_dir.py"):
            continue
        path_dir = os.path.join(direct_dir, fname)
        path_cot = os.path.join(cot_dir, fname.replace("_dir", "_CoT"))

        res = evaluate(fname, path_dir, path_cot)
        if res:
            results.append(res)

    out_path = os.path.join(batch_dir, "functionality_results.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["problem_id", "direct_passed", "cot_passed", "total"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n Functionality evaluation completed. Saved to {out_path}")

    return out_path, results

evaluate_all()
