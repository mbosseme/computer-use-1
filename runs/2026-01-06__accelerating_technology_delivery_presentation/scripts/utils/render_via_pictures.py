# Final wrapper: 
# 1. Renders to ~/Pictures/AgentRenderTemp using AppleScript
# 2. Moves content to expected run folder
# 3. Cleans up Pictures

import os
import shutil
import subprocess
import sys

APPLESCRIPT_PICTURES = """
on run argv
    set pptxPath to item 1 of argv
    
    -- Target ~/Pictures/AgentRenderTemp
    set mkDirCmd to "mkdir -p ~/Pictures/AgentRenderTemp"
    do shell script mkDirCmd
    
    set targetFolder to (path to pictures folder as string) & "AgentRenderTemp"
    
    tell application "Microsoft PowerPoint"
        activate
        open (POSIX file pptxPath)
        set thePres to the active presentation
        
        -- Save
        save thePres in targetFolder as save as PNG
        
        close thePres saving no
    end tell
end run
"""

def render_via_pictures(pptx_path, dest_dir):
    abs_pptx = os.path.abspath(pptx_path)
    abs_dest = os.path.abspath(dest_dir)
    
    # 1. Clean destination
    if os.path.exists(abs_dest):
        shutil.rmtree(abs_dest)
    os.makedirs(abs_dest, exist_ok=True)
    
    # 2. Write Script
    script_path = os.path.join(os.path.dirname(__file__), "render_pics.scpt")
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_PICTURES)
        
    print(f"Rendering via Pictures relay...")
    subprocess.run(["osascript", script_path, abs_pptx])
    
    # 3. Move files
    pics_dir = os.path.expanduser("~/Pictures/AgentRenderTemp")
    
    # It might create a subfolder named after the presentation "draft_v1_branded"
    pres_name = os.path.splitext(os.path.basename(abs_pptx))[0]
    possible_subfolder = os.path.join(pics_dir, pres_name)
    
    source = None
    if os.path.exists(possible_subfolder):
        source = possible_subfolder
    elif os.path.exists(pics_dir):
        # Check if files are directly there
        if any(f.endswith(".PNG") for f in os.listdir(pics_dir)):
            source = pics_dir
            
    if source:
        print(f"Found renders in {source}, moving to {abs_dest}")
        for item in os.listdir(source):
            if item.endswith(".PNG") or item.endswith(".png"):
                shutil.move(os.path.join(source, item), abs_dest)
        # Cleanup
        shutil.rmtree(pics_dir)
    else:
        print("Error: Could not locate rendered files in Pictures folder.")
        
    if os.path.exists(script_path):
        os.remove(script_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 render_pics.py <input.pptx> <output_dir>")
    else:
        render_via_pictures(sys.argv[1], sys.argv[2])
