# Alternate AppleScript using `export` command which is cleaner if supported
# and explicitly creating the directory if needed via shell
APPLESCRIPT_EXPORT = """
on run argv
    set pptxPath to item 1 of argv
    set outputFolder to item 2 of argv
    
    set pptxPosixPath to POSIX file pptxPath
    set outputPosixFolder to POSIX file outputFolder
    
    tell application "Microsoft PowerPoint"
        activate
        open pptxPosixPath
        set thePres to the active presentation
        
        -- Retry simple Save As PNG without the 'save as' keyword repetition which might be the syntax error
        -- Syntax: save thePres in <file> as <file type>
        
        save thePres in outputPosixFolder as save as PNG
        
        close thePres saving no
    end tell
end run
"""
import os
import subprocess
import sys

def render_deck_alt(pptx_path, output_dir):
    abs_pptx_path = os.path.abspath(pptx_path)
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)
    
    script_path = os.path.join(os.path.dirname(__file__), "render_slides_alt.scpt")
    
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_EXPORT)
        
    print(f"Rendering (Alt) {abs_pptx_path} to {abs_output_dir}...")
    
    try:
        cmd = ["osascript", script_path, abs_pptx_path, abs_output_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            print("Render complete.")
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

if __name__ == "__main__":
    render_deck_alt(sys.argv[1], sys.argv[2])
