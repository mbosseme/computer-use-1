import pandas as pd
import re
from pathlib import Path

# Paths
RUN_ID = "2026-01-27__fy27-email-handoff"
EXPORTS_DIR = Path(f"runs/{RUN_ID}/exports")
ORIGINAL_CSV = EXPORTS_DIR / "iv_solutions__external_sample_enriched.csv"
GAP_CSV = EXPORTS_DIR / "iv_solutions__gap_products.csv"
DICT_MD = EXPORTS_DIR / "iv_solutions__external_sample_enriched_dictionary.md"
OUTPUT_XLSX = EXPORTS_DIR / "Fresenius_IV_Solutions_Data_Pack_FY27.xlsx"

def parse_markdown_dictionary(md_path):
    """
    Simple parser to convert the Markdown data dictionary into a DataFrame.
    """
    if not md_path.exists():
        return pd.DataFrame({"Info": ["Dictionary file not found."]})

    lines = md_path.read_text().splitlines()
    data = []
    
    # We will just grab the table rows
    # Regex for table row: starts and ends with |
    table_row_re = re.compile(r"^\|(.*)\|$")
    
    current_section = "General"
    
    for line in lines:
        line = line.strip()
        if line.startswith("## "):
            current_section = line.replace("## ", "").strip()
            continue
            
        match = table_row_re.match(line)
        if match:
            # Split by pipe
            parts = [p.strip() for p in match.group(1).split("|")]
            # Skip header separator lines (---)
            if all("-" in p for p in parts):
                continue
            # Skip header lines themselves if we want a clean list, 
            # but actually let's just keep everything and filter later or just append
            if parts[0].lower() == "column": 
                continue # Skip header
                
            if len(parts) >= 2:
                col_name = parts[0].replace("`", "")
                desc = parts[1]
                data.append({
                    "Section": current_section,
                    "Column Name": col_name,
                    "Description": desc
                })
    
    return pd.DataFrame(data)

def main():
    print("Loading data...")
    
    # 1. Dictionary
    df_dict = parse_markdown_dictionary(DICT_MD)
    print(f"Loaded Dictionary: {len(df_dict)} rows")

    # 2. Original Extract
    if ORIGINAL_CSV.exists():
        df_orig = pd.read_csv(ORIGINAL_CSV)
        print(f"Loaded Original Extract: {len(df_orig)} rows")
    else:
        df_orig = pd.DataFrame({"Error": ["File not found"]})
        print("Warning: Original CSV not found.")

    # 3. Gap Analysis
    if GAP_CSV.exists():
        df_gap = pd.read_csv(GAP_CSV)
        print(f"Loaded Gap Analysis: {len(df_gap)} rows")
    else:
        df_gap = pd.DataFrame({"Error": ["File not found"]})
        print("Warning: Gap CSV not found.")

    # Write to Excel
    print(f"Writing to {OUTPUT_XLSX}...")
    with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
        
        # Tab 1: Data Dictionary
        df_dict.to_excel(writer, sheet_name="Data Dictionary", index=False)
        # Auto-adjust column widths (approximation)
        worksheet = writer.sheets["Data Dictionary"]
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 30
        worksheet.column_dimensions['C'].width = 80
        
        # Tab 2: Requested Products (Original)
        df_orig.to_excel(writer, sheet_name="Requested Products (Extract 1)", index=False)
        
        # Tab 3: Gap Products (New)
        df_gap.to_excel(writer, sheet_name="Gap Products (Extract 2)", index=False)

    print("Success! Workbook created.")

if __name__ == "__main__":
    main()
