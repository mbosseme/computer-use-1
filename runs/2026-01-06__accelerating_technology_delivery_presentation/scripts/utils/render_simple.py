# Last resort: Just use the documented 'save' command on the presentation object
# but assume it saves to the same directory as the file.
# This confirms if we can generate *any* PNGs, regardless of where they land.

APPLESCRIPT_SIMPLE_SAVE = """
on run argv
    set pptxPath to item 1 of argv
    
    tell application "Microsoft PowerPoint"
        activate
        open (POSIX file pptxPath)
        set thePres to the active presentation
        
        -- This command usually creates a folder named <Presentation> next to the file
        save thePres as save as PNG
        
        close thePres saving no
    end tell
end run
"""
import os
import subprocess
import sys

def render_simple(pptx_path):
    abs_pptx_path = os.path.abspath(pptx_path)
    
    script_path = os.path.join(os.path.dirname(__file__), "render_simple.scpt")
    
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_SIMPLE_SAVE)
        
    print(f"Rendering (Simple) {abs_pptx_path}...")
    
    cmd = ["osascript", script_path, abs_pptx_path]
    subprocess.run(cmd)
    
    if os.path.exists(script_path):
        os.remove(script_path)

if __name__ == "__main__":
    render_simple(sys.argv[1])
