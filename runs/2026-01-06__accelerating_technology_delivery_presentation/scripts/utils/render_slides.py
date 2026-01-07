import os
import sys
import subprocess
import shutil
from pdf2image import convert_from_path

# AppleScript to export slides as PDF
# This is explicitly known to work on this machine (see renders_v2_safe)
APPLESCRIPT_PDF_TEMPLATE = """
on run argv
    set pptxPath to item 1 of argv
    set pdfPath to item 2 of argv
    
    set pptxPosixPath to POSIX file pptxPath
    set pdfPosixPath to POSIX file pdfPath
    
    tell application "Microsoft PowerPoint"
        activate
        
        -- Try to open with a small delay to allow app wake-up
        try
            open pptxPosixPath
        on error errMsg
            error "Failed to open PPTX: " & errMsg
        end try
        
        set thePres to the active presentation
        
        -- EXPORT AS PDF
        save thePres in pdfPosixPath as save as PDF
        
        close thePres saving no
    end tell
end run
"""

def render_deck(pptx_path, output_dir):
    """
    Renders PPTX -> PDF (via AppleScript) -> PNGs (via pdf2image)
    Restored to the method used in 'renders_v2_safe'.
    """
    abs_pptx_path = os.path.abspath(pptx_path)
    abs_output_dir = os.path.abspath(output_dir)
    
    os.makedirs(abs_output_dir, exist_ok=True)
    temp_pdf_path = os.path.join(abs_output_dir, "_temp_render.pdf")
    
    # Clean previous temp file
    if os.path.exists(temp_pdf_path):
        os.remove(temp_pdf_path)
        
    print(f"[Stage 1] Exporting to PDF: {temp_pdf_path}")
    
    script_path = os.path.join(os.path.dirname(__file__), "export_pdf_temp.scpt")
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_PDF_TEMPLATE)
    
    try:
        # Run AppleScript
        cmd = ["osascript", script_path, abs_pptx_path, temp_pdf_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"CRITICAL: AppleScript Error: {result.stderr}")
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

    # Stage 2: PDF -> PNG
    print(f"[Stage 2] Converting PDF to PNGs...")
    
    try:
        images = convert_from_path(temp_pdf_path, thread_count=4)
        
        for i, image in enumerate(images):
            filename = f"slide_{i+1:02d}.png"
            dest_path = os.path.join(abs_output_dir, filename)
            image.save(dest_path, "PNG")
            # print(f"Saved {filename}") # Reduce noise
            
        print(f"Render complete. {len(images)} slides processed.")
        # Cleanup PDF
        # os.remove(temp_pdf_path) 
        return True
    
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python render_slides.py <pptx_path> <output_dir>")
        sys.exit(1)
        
    render_deck(sys.argv[1], sys.argv[2])
