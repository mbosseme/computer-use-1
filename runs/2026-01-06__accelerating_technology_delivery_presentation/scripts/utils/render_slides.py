import os
import sys
import subprocess
import shutil
from pdf2image import convert_from_path
from datetime import datetime

# AppleScript to export slides as PDF
# This is physically safer than image export due to Sandbox restrictions
APPLESCRIPT_PDF_TEMPLATE = """
on run argv
    set pptxPath to item 1 of argv
    set pdfPath to item 2 of argv
    
    set pptxPosixPath to POSIX file pptxPath
    set pdfPosixPath to POSIX file pdfPath
    
    tell application "Microsoft PowerPoint"
        activate
        open pptxPosixPath
        set thePres to the active presentation
        
        -- EXPORT AS PDF
        -- We use 'save as' with the PDF file format
        save thePres in pdfPosixPath as save as PDF
        
        close thePres saving no
    end tell
end run
"""

def render_deck(pptx_path, output_dir):
    """
    Renders PPTX -> PDF (via AppleScript) -> PNGs (via pdf2image)
    This avoids macOS Sandboxing issues with direct image export from PowerPoint.
    """
    abs_pptx_path = os.path.abspath(pptx_path)
    abs_output_dir = os.path.abspath(output_dir)
    
    # Define intermediate PDF path
    # We place it in the output dir to keep things self-contained
    os.makedirs(abs_output_dir, exist_ok=True)
    temp_pdf_path = os.path.join(abs_output_dir, "_temp_render.pdf")
    
    # -----------------------------
    # STAGE 1: PPTX -> PDF
    # -----------------------------
    print(f"[Stage 1] Exporting to PDF: {temp_pdf_path}")
    
    script_path = os.path.join(os.path.dirname(__file__), "export_pdf.scpt")
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_PDF_TEMPLATE)
    
    try:
        cmd = ["osascript", script_path, abs_pptx_path, temp_pdf_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error executing AppleScript: {result.stderr}")
            # Clean up and exit if PDF export fails
            if os.path.exists(script_path): os.remove(script_path)
            return False
            
    except Exception as e:
        print(f"Failed to run subprocess: {e}")
        return False
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

    if not os.path.exists(temp_pdf_path):
        print(f"Error: PDF file was not created at {temp_pdf_path}")
        return False

    # -----------------------------
    # STAGE 2: PDF -> PNG
    # -----------------------------
    print(f"[Stage 2] Converting PDF to PNGs in: {abs_output_dir}")
    
    try:
        # Convert PDF to images
        # thread_count=4 helps speed up rendering
        images = convert_from_path(temp_pdf_path, thread_count=4)
        
        for i, image in enumerate(images):
            # 1-based indexing for filenames
            filename = f"slide_{i+1:02d}.png"
            out_path = os.path.join(abs_output_dir, filename)
            image.save(out_path, "PNG")
            print(f"  Saved: {filename}")
            
    except Exception as e:
        print(f"Error converting using pdf2image: {e}")
        return False
    finally:
        # Cleanup intermediate PDF
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
            print("  Cleaned up temp PDF.")

    print(f"Render complete. Images available in {abs_output_dir}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 render_slides.py <input.pptx> [output_dir]")
        sys.exit(1)
        
    pptx_in = sys.argv[1]
    
    # If no output dir specified, create 'renders' sibling folder
    if len(sys.argv) > 2:
        dir_out = sys.argv[2]
    else:
        dir_out = os.path.join(os.path.dirname(pptx_in), "renders")
    
    render_deck(pptx_in, dir_out)
