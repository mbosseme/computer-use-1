import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Out-of-Band Data Validation Agent Runner")
    parser.add_argument("--artifact", required=True, help="Path to the artifact (e.g. .xlsx, .csv, .pdf) to validate")
    parser.add_argument("--persona", required=True, help="Path to a markdown file defining the agent persona")
    parser.add_argument("--schema", help="Path to a markdown file defining expected schema/structure")
    parser.add_argument("--heuristics", help="Path to a markdown file defining known traps and lessons learned", default="tools/validation_agent/known_traps.md")
    
    args = parser.parse_args()

    # Ensure files exist
    for filepath in [args.artifact, args.persona]:
        if not os.path.exists(filepath):
            print(f"Error: Required file not found: {filepath}", file=sys.stderr)
            sys.exit(1)

    template_parts = []
    
    with open(args.persona, 'r', encoding='utf-8') as f:
        template_parts.append(f"## ROLE & OBJECTIVE\n{f.read().strip()}")
        
    if args.schema and os.path.exists(args.schema):
        with open(args.schema, 'r', encoding='utf-8') as f:
            template_parts.append(f"## EXPECTED SCHEMA / STRUCTURE\n{f.read().strip()}")

    if args.heuristics and os.path.exists(args.heuristics):
        with open(args.heuristics, 'r', encoding='utf-8') as f:
            template_parts.append(f"## KNOWN TRAPS & HEURISTICS\n{f.read().strip()}")

    template_parts.append(f"## ARTIFACT UNDER TEST\nYou must evaluate the artifact located at: `{os.path.abspath(args.artifact)}`")
    
    template_parts.append(
        "## INSTRUCTIONS\n"
        "1. Open the artifact using python (matplotlib/pandas/openpyxl) or appropriate CLI tooling.\n"
        "2. Do NOT trust the pipeline logic that created this artifact. Read it objectively.\n"
        "3. Cross-reference the data payload against the schema and known traps.\n"
        "4. If you discover a completely new class of logic failure, explicitly state that it should be added to the KNOWN TRAPS file.\n"
        "5. Output your final audit notes outlining any anomalies, structural errors, or math disconnects."
    )

    full_prompt = "\n\n".join(template_parts)
    
    # Write the full prompt to a temporary file for the agent to consume
    prompt_file = "tmp_validation_prompt.md"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(full_prompt)

    print(f"[*] Built composite prompt inside {prompt_file}")
    print(f"[*] Launching generic validation agent via GitHub Copilot CLI...")

    # We use the standard runSubagent execution pattern via the host environment, 
    # but since this is a python script, we print instructions to the user.
    print("\n--------------------------------------------------")
    print("To invoke the autonomous agent, run the following in your Copilot Chat / Agent interface:")
    print(f"\"@github Please act as the out-of-band validation agent. Read the prompt in {prompt_file} and execute the validation exactly as described.\"")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()