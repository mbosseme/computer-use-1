import docx
doc_path = "/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notetaking/Meeting Notes/2026/03/10/2026-03-10 1300 - SC Internal Deal Desk Project Meeting - Danielle-Bill-Matthew - eid9d3d92a8.docx"
doc = docx.Document(doc_path)
print([p.text for p in doc.paragraphs if 'Teams Recap' in p.text])
