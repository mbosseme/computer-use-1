import re

input_path = "scripts/profiling_premier.sql"

with open(input_path, "r") as f:
    content = f.read()

# Replace batch separators with UNION ALL
# Pattern: \n\s*-- END BATCH --\s*\n\s*-- Batch \d+: .*?\n
fixed_content = re.sub(
    r"\n\s*-- END BATCH --\s*\n\s*-- Batch \d+: .*?\n", 
    "\nUNION ALL\n", 
    content,
    flags=re.MULTILINE
)

with open(input_path, "w") as f:
    f.write(fixed_content)

print(f"Fixed content, length: {len(fixed_content)}")
