#!/bin/bash
cd /Users/matt_bossemeyer/Projects/wt-2026-03-04__portfolio-competitiveness/dataform
npx --no-install @dataform/cli run
cd ..
python3 scripts/export_deliverable.py
