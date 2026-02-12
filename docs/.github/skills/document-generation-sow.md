# Skill: Document Generation (SOW / Legal)

This skill outlines the process for drafting, refining, and generating formal Statement of Work (SOW) documents in the Premier Standard format.

## 1. Context & Use Case
*   **Trigger:** User requests to draft, update, or export a Statement of Work (SOW) or similar legal/contractual document.
*   **Standard:** Use "Premier Standard" formatting (managed via `templates/Premier_Standard_Legal.dotx`).
*   **Key Risks:** Ambiguous commercial terms ("best effort"), undefined spend commitments, misaligned "PO vs Invoice" expectations.

## 2. Process Workflow

### Phase A: Drafting & Refinement
1.  **Start with Markdown:** Draft the content in Markdown first for easy iteration.
2.  **Second Opinion Check:** Before finalizing, ask for a "Second Opinion" or critique of the SOW against known risks (e.g., transcripts of negotiation calls, "soft" commitments).
    *   *Self-Correction:* If the SOW says "User will provide data," ask "What happens if they don't? Is there a timeline penalty?"
3.  **Pricing Tables:** Ensure pricing tables capture:
    *   Core Fee (One-time vs. Recurring).
    *   Renewal Fee (Year 2+).
    *   Add-ons explicitly separated.

### Phase B: Document Generation (Technical)
We use a custom tool to handle the conversion because the standard `python-docx` library does not natively support `.dotx` templates.

**Tool Location:** `tools/generate_docx.py`
**Template Location:** `templates/Premier_Standard_Legal.dotx`

**Command:**
```bash
python tools/generate_docx.py --input <your_draft.md> --template templates/Premier_Standard_Legal.dotx --output <output_filename.docx>
```

## 3. Technical Constraints & Rules
The generating script handles several specific "gotchas" that you do NOT need to reimplement manually:
1.  **Dotx Handling:** It automatically unzips and converts `.dotx` to `.docx` XML structure on the fly.
2.  **Content Clearing:** It removes the Latin placeholder text (`lorem ipsum`) from the template automatically.
3.  **Section Properties:** It preserves `sectPr` (margins, orientation, paper size), so the final doc matches the corporate standard.

### Style Mapping (Markdown -> Word)
The tool maps Markdown elements to specific Word styles. If you customize the tool, maintain these mappings:
*   `# Title` -> **Heading 1** (Not 'Title', which is often missing in legal templates).
*   `## Section` -> **Heading 2**
*   `### Subsection` -> **Heading 3**
*   `| Table |` -> **Table Grid**

## 4. Recovery Rules
*   **Error: "No style with name 'Title'"**: This happens if the template lacks a generic Title style. *Fix:* ensure the script maps Level 0 headers to 'Heading 1'.
*   **Error: "IndexError: list index out of range"**: This often happens when clearing body elements if you accidentally remove the `sectPr` element. *Fix:* Ensure the script filters out `sectPr` during content deletion.
