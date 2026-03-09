import subprocess
try:
    print("Running dataform via subprocess...")
    result = subprocess.run(["npx", "@dataform/cli", "run"], cwd="/Users/matt_bossemeyer/Projects/wt-2026-03-04__portfolio-competitiveness/dataform", capture_output=True, text=True, check=True)
    with open("dataform_success.log", "w") as f:
        f.write(result.stdout)
    print("Success. Output written to dataform_success.log")
except subprocess.CalledProcessError as e:
    with open("dataform_success.log", "w") as f:
        f.write("FAIL\n\nSTDOUT:\n")
        f.write(e.stdout)
        f.write("\n\nSTDERR:\n")
        f.write(e.stderr)
    print("Failed")
