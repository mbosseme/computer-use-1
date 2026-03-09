import subprocess
import sys

print("Running Dataform...")
try:
    subprocess.run(["npx", "--no-install", "@dataform/cli", "run"], cwd="/Users/matt_bossemeyer/Projects/wt-2026-03-04__portfolio-competitiveness/dataform", check=True)
    print("Dataform OK.")
except subprocess.CalledProcessError as e:
    print("Dataform failed!")
    sys.exit(1)

print("\nRunning Export...")
try:
    subprocess.run(["python3", "scripts/export_deliverable.py"], cwd="/Users/matt_bossemeyer/Projects/wt-2026-03-04__portfolio-competitiveness", check=True)
    print("Export OK.")
except subprocess.CalledProcessError as e:
    print("Export failed!")
    sys.exit(1)
