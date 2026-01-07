# Last resort: Python-based loop over slides using `export slide X as ...`
# This iterates through slides 1..N and saves each individually to rule out "bulk save" issues.

APPLESCRIPT_ITERATIVE = """
on run argv
    set pptxPath to item 1 of argv
    set outputFolder to item 2 of argv
    
    set pptxPosixPath to POSIX file pptxPath
    set outputPosixFolder to POSIX file outputFolder
    
    tell application "Microsoft PowerPoint"
        activate
        open pptxPosixPath
        set thePres to the active presentation
        
        repeat with i from 1 to count of slides of thePres
            set theSlide to slide i of thePres
            set fileName to outputFolder & "/Slide_" & i & ".png"
            
            -- "save" command with save as PNG enum
            -- 'save as PNG' is a specific command constant often required
            
            save theSlide in fileName as save as PNG
        end repeat
        
        close thePres saving no
    end tell
end run
"""
import os
import subprocess
import sys

def render_iterative(pptx_path, output_dir):
    abs_pptx_path = os.path.abspath(pptx_path)
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)
    
    script_path = os.path.join(os.path.dirname(__file__), "render_iterative.scpt")
    
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_ITERATIVE)
        
    print(f"Rendering (Iterative) {abs_pptx_path} to {abs_output_dir}...")
    
    cmd = ["osascript", script_path, abs_pptx_path, abs_output_dir]
    subprocess.run(cmd)
    
    if os.path.exists(script_path):
        os.remove(script_path)

if __name__ == "__main__":
    render_iterative(sys.argv[1], sys.argv[2])
