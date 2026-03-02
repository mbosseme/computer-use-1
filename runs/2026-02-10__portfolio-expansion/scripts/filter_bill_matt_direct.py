from pathlib import Path
import json

repo = Path(__file__).resolve().parents[3]
base = repo / "runs" / "2026-02-10__portfolio-expansion" / "exports"
src = base / "bill_matt_last_2_months_graph.json"
rows = json.loads(src.read_text(encoding="utf-8"))

matt = "matt_bossemeyer@premierinc.com"
bill = "bill_marquardt@premierinc.com"

def participants(row):
    p = set()
    sender = ((row.get("from") or {}).get("address") or "").lower()
    if sender:
        p.add(sender)
    for name, addr in row.get("to", []):
        if addr:
            p.add(addr.lower())
    for name, addr in row.get("cc", []):
        if addr:
            p.add(addr.lower())
    return p

out = []
for row in rows:
    sender = ((row.get("from") or {}).get("address") or "").lower()
    p = participants(row)
    if sender == matt and bill in p:
        out.append(row)
    elif sender == bill and matt in p:
        out.append(row)

json_path = base / "bill_matt_direct_last_2_months_graph.json"
json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

md_path = base / "bill_matt_direct_last_2_months_graph.md"
lines = [
    "# Bill ↔ Matt Direct Exchange (Last 2 Months)",
    f"_Message count: {len(out)}_",
    "",
]
for row in out:
    frm = row.get("from") or {}
    to = ", ".join([f"{n} <{a}>" if n and n != a else a for n, a in row.get("to", [])])
    cc = ", ".join([f"{n} <{a}>" if n and n != a else a for n, a in row.get("cc", [])])
    lines.extend(
        [
            f"## {row.get('subject') or '(no subject)'}",
            f"- Sent: {row.get('sentDateTime')}",
            f"- Received: {row.get('receivedDateTime')}",
            f"- From: {(frm.get('name') or '')} <{(frm.get('address') or '')}>",
            f"- To: {to}",
            f"- Cc: {cc}",
            "",
            "### Preview",
            row.get("bodyPreview") or "",
            "",
        ]
    )
md_path.write_text("\n".join(lines), encoding="utf-8")

print(json_path)
print(md_path)
print(f"direct={len(out)}")
