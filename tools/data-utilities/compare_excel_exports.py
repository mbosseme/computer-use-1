#!/usr/bin/env python3
"""
Compare Two Excel Exports (QA Utility)

Generalized version of `qa_national_aggregate.py` for comparing ANY two Excel files 
often produced by data extraction runs.

Usage:
    python tools/data-utilities/compare_excel_exports.py \
        --old path/to/old.xlsx --new path/to/new.xlsx \
        --old-sheet "Sheet1" --new-sheet "Sheet1" \
        --join-col "ndc11" --metric-col "spend"

"""
import argparse
import pandas as pd
from pathlib import Path
import sys

def compare_sheets(old_path, new_path, old_sheet, new_sheet, join_col=None, metric_col=None):
    print(f"\n### Comparing Sheets: '{old_sheet}' vs '{new_sheet}'")
    
    try:
        old_df = pd.read_excel(old_path, sheet_name=old_sheet)
        new_df = pd.read_excel(new_path, sheet_name=new_sheet)
    except Exception as e:
        print(f"Error loading sheets: {e}")
        return

    # Basic Stats
    stats = {}
    stats['Old Rows'] = len(old_df)
    stats['New Rows'] = len(new_df)
    
    # Optional Metric comparison
    if metric_col:
        col_clean = metric_col.strip()
        if col_clean in old_df.columns and col_clean in new_df.columns:
            stats['Old Metric'] = old_df[col_clean].sum()
            stats['New Metric'] = new_df[col_clean].sum()
            stats['Diff'] = stats['New Metric'] - stats['Old Metric']
            if stats['Old Metric'] != 0:
                stats['Match %'] = (stats['New Metric'] / stats['Old Metric']) * 100
            else:
                stats['Match %'] = 0.0
        else:
            stats['Metric Check'] = f"Column '{col_clean}' missing in one or both files."

    # Print Table
    print(f"{'Metric':<25} | {'Old File':<15} | {'New File':<15} | {'Diff / Notes':<15}")
    print("-" * 75)
    print(f"{'Row Count':<25} | {stats['Old Rows']:<15} | {stats['New Rows']:<15} | {stats['New Rows'] - stats['Old Rows']}")
    
    if metric_col and 'Old Metric' in stats:
        print(f"{'Metric Sum':<25} | {stats['Old Metric']:<14,.2f} | {stats['New Metric']:<14,.2f} | {stats['Diff']:,.2f} ({stats['Match %']:.1f}%)")

    # Join Column Analysis (Unique IDs)
    if join_col:
        jc = join_col.strip()
        if jc in old_df.columns and jc in new_df.columns:
            old_set = set(old_df[jc].unique())
            new_set = set(new_df[jc].unique())
            
            missing = old_set - new_set
            extra = new_set - old_set
            
            print(f"{'Distinct Keys ('+jc+')':<25} | {len(old_set):<15} | {len(new_set):<15} | {len(new_set) - len(old_set)}")
            
            if missing:
                print(f"\nWARNING: {len(missing)} keys in Old but missing in New.")
                print(f"Examples: {list(missing)[:5]}")
            if extra:
                print(f"\nINFO: {len(extra)} keys in New but missing in Old.")
                print(f"Examples: {list(extra)[:5]}")
        else:
            print(f"\nJoin column '{jc}' not found in both sheets.")

def main():
    parser = argparse.ArgumentParser(description="Compare two Excel exports.")
    parser.add_argument("--old", required=True, help="Path to old Excel file")
    parser.add_argument("--new", required=True, help="Path to new Excel file")
    parser.add_argument("--old-sheet", required=True, help="Sheet name in Old file")
    parser.add_argument("--new-sheet", required=True, help="Sheet name in New file")
    parser.add_argument("--join-col", help="Column to compare distinct selection (e.g. ndc11)")
    parser.add_argument("--metric-col", help="Column to sum check (e.g. spend)")
    
    args = parser.parse_args()
    
    old_p = Path(args.old)
    new_p = Path(args.new)
    
    if not old_p.exists():
        print(f"Old file not found: {old_p}")
        sys.exit(1)
    if not new_p.exists():
        print(f"New file not found: {new_p}")
        sys.exit(1)
        
    compare_sheets(
        old_p, new_p,
        args.old_sheet, args.new_sheet,
        args.join_col, args.metric_col
    )

if __name__ == "__main__":
    main()
