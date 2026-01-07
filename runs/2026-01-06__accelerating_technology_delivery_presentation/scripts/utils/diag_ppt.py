# Simple diagnostic script to see where PowerPoint saves files by default
APPLESCRIPT_DIAG = """
on run argv
    set pptxPath to item 1 of argv
    set pptxPosixPath to POSIX file pptxPath
    
    tell application "Microsoft PowerPoint"
        activate
        open pptxPosixPath
        set thePres to the active presentation
        
        -- Try saving without a path to see if it defaults to Documents or the file dir
        -- Or try getting the 'full name' property
        
        log (get full name of thePres)
        
        close thePres saving no
    end tell
end run
"""
import os
import subprocess
import sys

def diag(pptx_path):
    script_path = "diag.scpt"
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_DIAG)
    
    cmd = ["osascript", script_path, os.path.abspath(pptx_path)]
    subprocess.run(cmd)
    
    if os.path.exists(script_path):
        os.remove(script_path)

if __name__ == "__main__":
    diag(sys.argv[1])
