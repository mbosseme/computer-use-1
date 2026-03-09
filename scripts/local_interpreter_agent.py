import json
import re
import sys
import subprocess
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from agent_tools.llm.azure_openai_responses import AzureOpenAIResponsesClient
from agent_tools.llm.smoketest import _resolve_azure_config

def execute_python_code(code: str) -> str:
    """Execute Python code locally and return stdout/stderr."""
    temp_script = Path("scripts/.tmp_qa_code.py")
    with temp_script.open("w", encoding="utf-8") as f:
        f.write("import pandas as pd\n")
        f.write("import warnings\n")
        f.write("warnings.filterwarnings('ignore')\n")
        f.write("import sys\n")
        f.write("sys.stdout.reconfigure(encoding='utf-8')\n")
        f.write(code)
    
    try:
        # Give it a very generous timeout since it's a 200k row Excel file
        result = subprocess.run(
            [sys.executable, str(temp_script)],
            capture_output=True,
            text=True,
            timeout=180, 
            cwd=str(repo_root)
        )
        output = result.stdout
        if result.stderr:
            output += "\nSTDERR:\n" + result.stderr
            
        print(f"[Subprocess finished. Output length: {len(output)}]")
        return output[:8000] # Truncate to avoid context blowout
    except subprocess.TimeoutExpired:
        return "ERROR: Execution timed out (took > 180 seconds). The file might be too big to load all at once. Try specifying `sheet_name` and `nrows`."
    except Exception as e:
        return f"ERROR: Execution failed: {e}"

def extract_code_block(text: str) -> str:
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def main():
    print("Initializing Local Code Interpreter loop for GPT-5.4...")
    
    system_prompt = """You are "The Skeptical Contract Director," a cynical healthcare supply-chain data QA expert.

Mission:
- Determine whether the output workbook `runs/2026-03-04__portfolio-competitiveness/HCIQ_Benchmark_Analysis_Deliverable.xlsx` is business-plausible.
- Find relationship anomalies that would mislead an executive dashboard. 
- Ensure mapping limits (LOCAL/REGIONAL restrictions, 80% coverage parity rule) are met.

RESOURCES:
You have a LOCAL PYTHON CODE INTERPRETER. 
If you need to analyze the data, you MUST write python code using pandas. 
The Excel file is massive (~200,000 rows). ALWAYS use `pd.read_excel('runs/2026-03-04__portfolio-competitiveness/HCIQ_Benchmark_Analysis_Deliverable.xlsx', sheet_name='...')` instead of `pd.ExcelFile` to avoid timeouts. 
The tabs are:
1. 'Tab A - Program Summary'
2. 'Tab B - Contract Summary'
3. 'Tab C - Item Drilldown'

To run code, reply strictly with a markdown Python block starting with ```python
Always print() your findings so you can read them. Do not write interactive code.
Wait for the system to provide the output of your code before continuing. Validate:
1. Reconciliation Check (sums match).
2. Missing benchmarks causing "$0 target" inflation.
3. Implausible savings/UOM variance.
4. Total benchmark coverage is >= 80%.

When you have collected enough evidence, output your final findings using a markdown block starting with ```markdown
"""

    messages = [
        {"role": "user", "content": "Begin your investigation of the workbook. Write a python script to inspect Tab A and Tab B, and I will run it and give you the output."}
    ]

    try:
        cfg = _resolve_azure_config(model_name="azure-gpt-5.4")
        client = AzureOpenAIResponsesClient(cfg)
    except Exception as e:
        print(f"Failed to load Azure OpenAI Config: {e}")
        return 1

    max_turns = 10
    
    for turn in range(max_turns):
        print(f"\n--- Turn {turn + 1} ---")
        
        # Build input_data array manually to map Azure 'assistant' output_text format properly
        input_data = []
        for msg in messages:
            r = msg["role"]
            c = msg["content"]
            out_msg = {"type": "message", "role": r}
            if r == "assistant":
                out_msg["content"] = [{"type": "output_text", "text": c}]
            else:
                out_msg["content"] = [{"type": "input_text", "text": c}]
            input_data.append(out_msg)
            
        print("Waiting for GPT-5.4...")
        result = client.create_response(
            input_data=input_data,
            instructions=system_prompt,
            max_output_tokens=4000,
            reasoning_effort="high",
            timeout_s=180
        )
        
        output_text = client.extract_output_text(result)
        
        if not output_text:
            print(f"API Returned empty text. Raw Result: {result}")
            break
            
        print("\n[GPT-5.4 Output]:")
        # Print a short preview
        preview = output_text[:800] + ("..." if len(output_text) > 800 else "")
        print(preview)
        
        messages.append({"role": "assistant", "content": output_text})
        
        # Check if the model is producing the final report
        if "```markdown" in output_text:
            match = re.search(r"```markdown\n(.*?)\n```", output_text, re.DOTALL)
            if match:
                report = match.group(1)
            else:
                report = output_text
                
            out_file = Path("runs/2026-03-04__portfolio-competitiveness/notes/agent-runs/2026-03-08_GPT_5_4_Skeptical_QA_Report.md")
            with open(out_file, "w") as f:
                f.write(report)
            print(f"\n[SUCCESS] Final Report saved to {out_file}")
            break
            
        # Check if model wants to run python code
        code_to_run = extract_code_block(output_text)
        if code_to_run:
            print("\n[Executing Code Interpreter...]")
            output = execute_python_code(code_to_run)
            feed_back = f"Code Output:\n```\n{output}\n```"
            print(feed_back[:500] + "...")
            messages.append({"role": "user", "content": feed_back})
        else:
            messages.append({"role": "user", "content": "I did not detect a ```python block or a ```markdown block. Please execute a query or finalize the report using the instructed markdown."})
            
    print("\nRun complete.")

if __name__ == "__main__":
    sys.exit(main())