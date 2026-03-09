import subprocess
import re

html_content = """<div style="font-family: Calibri, sans-serif; font-size: 11pt; color: #000;">
<p>Hi Joe,</p>

<p>Thanks for the feedback and the mockup! Before jumping into the visualization, I wanted to provide a quick update on the main <em>HCIQ Benchmark Analysis</em> deliverable. I made some additional Q/A passes over the weekend, and it feels fairly tight now. The latest version is uploaded to the same OneDrive folder you've been accessing.</p>

<p>A few improvements we implemented since my earlier email to further solidify the underlying data:</p>
<ul style="margin-top: 0; margin-bottom: 10px;">
    <li><strong>UOM Data Quality Guardians:</strong> We implemented bounds testing to prevent unit-of-measure mismatches (where a box/case conversion error might blow up variance) from artificially inflating opportunity sizing.</li>
    <li><strong>Weighted Program Summaries:</strong> Program-level summarizations are now strictly weighted against <em>benchmarked spend</em>&mdash;meaning un-benchmarked ("unknown") data is safely ignored to prevent metrics dilution.</li>
    <li><strong>Pricing QA Context:</strong> We added an <code>Average_Purchase_Price_6mo</code> field to the QA exceptions tab so that actual hospital purchasing behaviors can be instantly cross-referenced against the stated contract tier.</li>
</ul>

<hr style="border: none; border-top: 1px solid #ccc; margin: 20px 0;" />

<h3>FY27 Opportunity Timing &amp; Visualization</h3>

<p>With the core data stabilized, I love the concept you sketched out for mapping performance. I've put together a refreshed bubble chart based on that direction, focusing specifically on our <strong>FY27 contract expirations</strong> (July 1, 2026 - June 30, 2027) so we can look ahead.</p>

<p>We've exported the detailed tracking for this specific cohort in a complementary Excel workbook (<code>FY27_Contract_Competitive_Heat_Map.xlsx</code>, also in OneDrive). For clarity, since our scope here is forward-looking for the next fiscal year, the figures below represent our <strong>annualized estimates</strong> for this specific subset of expiring contracts:</p>
<ul style="margin-top: 0; margin-bottom: 10px;">
    <li><strong>National (Target: 25th):</strong> 425 contracts | \$5.06B Annualized Benchmarked Spend | <strong>\$1.0B Target Gap</strong> (19.8%)</li>
    <li><strong>Surpass (Target: Low):</strong> 34 contracts | \$867M Annualized Benchmarked Spend | <strong>\$106M Target Gap</strong> (12.2%)</li>
    <li><strong>Ascend Drive (Target: 10th):</strong> 56 contracts | \$288M Annualized Benchmarked Spend | <strong>\$30M Target Gap</strong> (10.5%)</li>
</ul>

<p>Below is the updated chart. Instead of graphing raw percentile, I plotted the <em>continuous gap to our benchmark targets</em> on the Y-Axis. This uses the exact targeting thresholds you outlined previously (Surpass at Low, AD at 10th, National at 25th). This absolute gap approach puts performance in direct, actionable terms instead of general percentiles. The bubbles are sized by total dollar opportunity, and I've abbreviated the longest contract names to keep things readable.</p>

<p><img src="cid:opportunity_chart" alt="FY27 Opportunity Timing Bubble Chart" style="max-width: 900px; height: auto;"/></p>

<p>Let me know what you think of this approach.</p>

<p>Lastly, regarding your thought earlier in the thread on recent contract launches&mdash;I completely agree that annualizing those will disproportionately weight their percentiles. It's a valid point and a refinement we should build into the logic over time. However, I don't think we need to push that complexity in right away, as these recent contracts won't be key targets in the coming year (they won't be renegotiated for a while), and their overall influence on the macro program summary is relatively small. But as we begin evaluating contracts at the individual manager level, we can absolutely account for those recent launch windows where appropriate.</p>

<p>Thanks again, and looking forward to your thoughts!</p>

<p>Best,<br/>Matt</p>
</div>"""

with open('runs/2026-03-04__portfolio-competitiveness/draft_body.html', 'w') as f:
    f.write(html_content)

print("Creating base reply draft...")
res = subprocess.run(
    ['python3', 'agent_tools/graph/create_draft_from_md.py', 
     '--md', 'runs/2026-03-04__portfolio-competitiveness/draft_to_joe.md', 
     '--reply-to', 'AAMkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwBGAAAAAAAlR3BCNHUoR42P4-xIVEVaBwCtC60M6iwCT6oV7C2g6lbxAAAAQ-41AAAmYvJHuYjqQbIghoy3jqM-AAo_aAXHAAA='],
    capture_output=True, text=True, env={'PYTHONPATH': '.'}
)

print(res.stdout)
match = re.search(r'Message id: (\S+)', res.stdout)
if match:
    draft_id = match.group(1)
    print(f"Applying HTML/Image payload to draft {draft_id}...")
    res2 = subprocess.run(
        ['python3', 'scripts/update_outlook_draft_inline_evidence.py', 
         '--draft-id', draft_id, 
         '--images-json', 'runs/2026-03-04__portfolio-competitiveness/draft_images.json', 
         '--body-html', 'runs/2026-03-04__portfolio-competitiveness/draft_body.html', 
         '--preserve-quoted'],
        capture_output=True, text=True, env={'PYTHONPATH': '.'}
    )
    print(res2.stdout)
    if res2.stderr:
        print("Error:", res2.stderr)
    print("Draft updated successfully!")
else:
    print("Failed to obtain Draft ID.")
    print(res.stderr)
