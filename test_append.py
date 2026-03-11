import docx
from docx.shared import Inches

doc_path = "/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notetaking/Meeting Notes/2026/03/10/2026-03-10 1300 - SC Internal Deal Desk Project Meeting - Danielle-Bill-Matthew - eid9d3d92a8.docx"
doc = docx.Document(doc_path)

recap_found = False
for i, p in enumerate(doc.paragraphs):
    if p.text.startswith("Teams Recap Extraction"):
        # We will insert text right after the paragraph below the heading
        # Or wait, the prompt says "inject the verbatim Copilot extraction output under the Teams Recap Extraction section"
        recap_found = True
        break

if not recap_found:
    print("Could not find the 'Teams Recap Extraction' section in the document! This means the header isn't there.")
    # Actually wait, this doc was created BEFORE I added the headers!!!
    print("Oh, right, this doc was generated before I updated meeting_notes.py. Let me verify the new ones instead.")

