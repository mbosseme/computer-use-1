# Last resort for AppleScript: `export` verb on the presentation with explicit path
# Note: Newer PPT requires 'output file name' to be a folder for slides, or file for saving deck.

APPLESCRIPT_EXPORT_FORCE = """
on run argv
    set pptxPath to item 1 of argv
    
    tell application "Microsoft PowerPoint"
        activate
        open (POSIX file pptxPath)
        set thePres to the active presentation
        
        -- Try export to Pictures/ExportTest
        set targetFolder to (path to pictures folder as string) & "ExportTest"
        
        -- Create folder via Finder if needed? Python can do it, assumes existence.
        
        try
            -- 'save as' but pointing to the folder and specifying PNG via enumeration if possible
            -- This relies on the 'active presentation' implicit target mostly for older scripts, but let's try 'save in'
            
            save thePres in targetFolder as save as PNG
            log "Success: Saved to " & targetFolder
        on error errMsg
            log "Failed export: " & errMsg
        end try
        
        close thePres saving no
    end tell
end run
"""
import os
import subprocess
import sys

def force_export(pptx_path):
    # Ensure dir exists
    pics_dir = os.path.expanduser("~/Pictures/ExportTest")
    os.makedirs(pics_dir, exist_ok=True)
    
    script_path = "force_export.scpt"
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_EXPORT_FORCE)
        
    print(f"Running force export...")
    result = subprocess.run(["osascript", script_path, os.path.abspath(pptx_path)], capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    # Check results
    if os.path.exists(pics_dir):
        files = os.listdir(pics_dir)
        print(f"Files in {pics_dir}: {files}")
        
    if os.path.exists(script_path):
        os.remove(script_path)

if __name__ == "__main__":
    force_export(sys.argv[1])
