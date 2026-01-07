# Interactive Debugger for AppleScript
# This script opens PowerPoint and tries to save a single slide to the user's Pictures folder (standard sandbox hole)
# and prints every result code.

APPLESCRIPT_DEBUG = """
on run argv
    set pptxPath to item 1 of argv
    
    tell application "Microsoft PowerPoint"
        activate
        
        -- open command
        try
            open (POSIX file pptxPath)
            log "Opened presentation"
        on error errMsg
            log "Failed opening: " & errMsg
            return
        end try
        
        set thePres to the active presentation
        
        -- Try saving to Pictures (safe sandbox location usually)
        set targetPath to (path to pictures folder as string) & "Slide_Test.png"
        
        try
            -- 'save as PNG' enum specifically
            save slide 1 of thePres in targetPath as save as PNG
            log "Success: Saved to " & targetPath
        on error errMsg
            log "Failed saving: " & errMsg
        end try
        
        -- Keep open so we can inspect manually if needed
        -- close thePres saving no
    end tell
end run
"""

import os
import subprocess
import sys

def debug_ppt(pptx_path):
    script_path = "debug_ppt.scpt"
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_DEBUG)
        
    print(f"Running interactive debug...")
    result = subprocess.run(["osascript", script_path, os.path.abspath(pptx_path)], capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    if os.path.exists(script_path):
        os.remove(script_path)

if __name__ == "__main__":
    debug_ppt(sys.argv[1])
