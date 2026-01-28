#!/usr/bin/env python3
"""
run_full_pipeline.py — Orchestrates the full GE Market Insights pipeline.

Steps:
1. Runs Dataform to materialize tables.
2. Exports BigQuery tables to CSV artifacts in a new snapshot directory.
3. Generates Capital and Parity visuals.
4. Builds the PowerPoint deck (GE_PILOT_Validation.pptx).
5. Exports the deck to PDF.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

# Unset GOOGLE_APPLICATION_CREDENTIALS to use ADC (personal credentials)
# instead of any service account JSON that may be set in the parent environment.
# This is required for cross-project queries to abi-inbound-prod.
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

import pandas as pd
from google.cloud import bigquery

# Configuration
PROJECT_ID = "matthew-bossemeyer"  # Should ideally come from env or config
DATASET_MARTS = "ge_sample_marts"

def run_command(cmd, cwd=None, env=None):
    """Run a shell command and raise error if it fails."""
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd, env=env)

def ensure_snapshot_dir(run_id):
    """Create the snapshot directory."""
    snapshot_dir = Path("snapshots") / run_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "visuals").mkdir(parents=True, exist_ok=True)
    return snapshot_dir

def export_bigquery_tables(client, snapshot_dir):
    """Fetch BigQuery tables and save as CSVs expected by downstream scripts."""
    print("Exporting BigQuery tables to CSV...")

    # 1. mart_validation_mapping -> mart_validation_mapping_Provider_Reported_Data.csv
    query_val = f"SELECT * FROM `{PROJECT_ID}.{DATASET_MARTS}.mart_validation_mapping`"
    df_val = client.query(query_val).to_dataframe()
    df_val.to_csv(snapshot_dir / "mart_validation_mapping_Provider_Reported_Data.csv", index=False)
    print(f"Saved mart_validation_mapping ({len(df_val)} rows)")

    # 2. mart_observed_trends -> mart_observed_trends_Provider_Reported_Data.csv
    query_trends = f"SELECT * FROM `{PROJECT_ID}.{DATASET_MARTS}.mart_observed_trends`"
    df_trends = client.query(query_trends).to_dataframe()
    df_trends.to_csv(snapshot_dir / "mart_observed_trends_Provider_Reported_Data.csv", index=False)
    print(f"Saved mart_observed_trends ({len(df_trends)} rows)")

    # 3. Prepare CSVs for Deck Builder
    
    # slide_data_market_trends.csv (Same as mart_observed_trends but deck builder expects it)
    df_trends.to_csv(snapshot_dir / "slide_data_market_trends.csv", index=False)

    # slide_data_parity_validation.csv (From mart_parity_analysis)
    # Deck expects: Category, Transaction_Spend, Supplier_Spend
    query_parity = f"""
        SELECT 
            report_category as Category,
            SUM(transaction_spend) as Transaction_Spend,
            SUM(supplier_spend) as Supplier_Spend
        FROM `{PROJECT_ID}.{DATASET_MARTS}.mart_parity_analysis`
        GROUP BY 1
    """
    df_parity = client.query(query_parity).to_dataframe()
    df_parity.to_csv(snapshot_dir / "slide_data_parity_validation.csv", index=False)
    print(f"Saved slide_data_parity_validation.csv ({len(df_parity)} rows)")

    # slide_data_ct_breakout.csv (From mart_validation_mapping, filtered for CT)
    # Deck expects: Product_Description, manufacturer_normalized, total_observed_spend
    # And we should probably filter for CT category or similar
    df_ct = df_val[df_val['report_category'] == 'CT'].copy()
    df_ct.to_csv(snapshot_dir / "slide_data_ct_breakout.csv", index=False)
    print(f"Saved slide_data_ct_breakout.csv ({len(df_ct)} rows)")

def main():
    parser = argparse.ArgumentParser(description="Run full GE pipeline")
    parser.add_argument("--skip-dataform", action="store_true", help="Skip Dataform run")
    parser.add_argument(
        "--skip-charity-ct",
        action="store_true",
        help="Skip Charity CT presence/hierarchy outputs (ct_charity_*.csv)",
    )
    args = parser.parse_args()

    # 1. Generate Run ID
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"Starting Pipeline Run: {run_id}")
    
    snapshot_dir = ensure_snapshot_dir(run_id)
    print(f"Snapshot Directory: {snapshot_dir}")

    # 2. Run Dataform
    if not args.skip_dataform:
        print("Running Dataform...")
        # We need to run with tags 'ge_capital' AND 'parity' to ensure everything is built
        # Or just run all? The user said "full pipeline".
        # Let's run with both tags.
        # Note: Dataform CLI might not support multiple --tags flags additive nicely, 
        # but we can pass them as separate args or run twice.
        # Let's try running all relevant tags.
        run_command(["npx", "@dataform/cli", "run", "--tags", "ge_capital,parity"], cwd="dataform")

    # 3. Export Data
    client = bigquery.Client(project=PROJECT_ID)
    export_bigquery_tables(client, snapshot_dir)

    # 3b. Charity CT outputs (presence + hierarchy)
    if not args.skip_charity_ct:
        print("Generating Charity CT presence + hierarchy outputs...")
        # Note: ct_charity_outputs queries abi-inbound-prod tables, so we override
        # BIGQUERY_PROJECT_ID to run jobs from that project context (required for
        # cross-project query permissions when the data project restricts access).
        # Build a clean env: use ADC (user creds) not any service account,
        # and don't set BIGQUERY_PROJECT so the client uses ADC quota_project_id.
        clean_env = {k: v for k, v in os.environ.items() 
                     if k not in ("GOOGLE_APPLICATION_CREDENTIALS", "BIGQUERY_PROJECT")}
        clean_env["PYTHONPATH"] = "."
        run_command(
            [
                sys.executable,
                "scripts/ct_charity_outputs.py",
                "--snapshot-dir",
                str(snapshot_dir),
            ],
            env=clean_env,
        )

    # 4. Generate Visuals
    print("Generating Capital Visuals...")
    run_command([sys.executable, "scripts/generate_capital_visuals.py", "--run-id", run_id])
    
    # generate_parity_visuals is called by generate_capital_visuals, but let's be safe and ensure it runs
    # Actually, generate_capital_visuals.py has:
    # import generate_parity_visuals
    # generate_parity_visuals.generate_visuals(run_id)
    # So it should be covered.

    # 5. Build Deck
    print("Building PowerPoint Deck...")
    deck_output = snapshot_dir / "GE_PILOT_Validation.pptx"
    
    # We need to find the template path. 
    # Assuming it's in brand/Premier-FY25-PPT 16x9-Feb25.potx based on file list
    template_path = Path("brand/Premier-FY25-PPT 16x9-Feb25.potx")
    
    # Workaround: python-pptx sometimes struggles with .potx extension directly
    # Convert .potx to .pptx using soffice (LibreOffice) if available
    temp_template = snapshot_dir / "template_base.pptx"
    
    try:
        print("Converting template .potx to .pptx using soffice...")
        cmd_convert = [
            "soffice", 
            "--headless", 
            "--convert-to", "pptx", 
            str(template_path), 
            "--outdir", str(snapshot_dir)
        ]
        subprocess.run(cmd_convert, check=True, capture_output=True)
        
        # soffice output filename might be different, usually same name but new extension
        # Premier-FY25-PPT 16x9-Feb25.pptx
        converted_name = template_path.with_suffix(".pptx").name
        converted_path = snapshot_dir / converted_name
        
        if converted_path.exists():
            # Rename to what we expect
            converted_path.rename(temp_template)
        else:
            print(f"Warning: Converted file {converted_name} not found. Using copy method.")
            import shutil
            shutil.copy(template_path, temp_template)
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: soffice not found or failed. Falling back to direct copy (might fail if python-pptx is strict).")
        import shutil
        shutil.copy(template_path, temp_template)
    
    cmd_deck = [
        sys.executable, 
        "src/pptx_builder/build_ge_deck.py",
        "--snapshot-dir", str(snapshot_dir),
        "--out", str(deck_output),
        "--template", str(temp_template)
    ]
    run_command(cmd_deck, env={**os.environ, "PYTHONPATH": "."})

    print(f"Pipeline Complete. Artifacts in {snapshot_dir}")

if __name__ == "__main__":
    main()
