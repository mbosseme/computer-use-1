cd dataform
npx --no-install @dataform/cli run > run_log.txt 2>&1
cd ..
python3 scripts/export_deliverable.py > export_log.txt 2>&1
echo "Finished all" > done.txt
