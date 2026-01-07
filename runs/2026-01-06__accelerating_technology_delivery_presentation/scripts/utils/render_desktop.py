# scripts/utils/render_desktop.py
import os
import subprocess
import shutil
import sys

APPLESCRIPT_DESKTOP = """
on run argv
    set pptxPath to item 1 of argv
    set pptxPosixPath to POSIX file pptxPath
    
    -- Target the user Desktop explicitly
    set desktopPath to (path to desktop as string) & "Agent_Render_Temp"
    
    tell application "Microsoft PowerPoint"
        activate
        open pptxPosixPath
        set thePres to the active presentation
        
        -- Save as PNG to the Desktop folder
        save thePres in desktopPath as save as PNG
        
        close thePres saving no
    end tell
end run
"""

def render_via_desktop(pptx_path, final_dest):
    abs_pptx = os.path.abspath(pptx_path)
    abs_dest = os.path.abspath(final_dest)
    
    # 1. Write script
    script_path = "render_desktop.scpt"
    with open(script_path, "w") as f:
        f.write(APPLESCRIPT_DESKTOP)
        
    print(f"Rendering via Desktop relay...")
    subprocess.run(["osascript", script_path, abs_pptx])
    
    # 2. Move from Desktop to run folder
    desktop = os.path.expanduser("~/Desktop")
    # Note: Microsoft PowerPoint often appends "1" or similar if folder exists, 
    # but "Agent_Render_Temp" is the target *file* path for the save command, which creates a folder.
    # Standard behavior is creating a folder named "Agent_Render_Temp" containing Slide1.PNG etc.
    src_folder = os.path.join(desktop, "Agent_Render_Temp")
    
    if os.path.exists(src_folder):
        print(f"Moving renders to {abs_dest}")
        if os.path.exists(abs_dest):
            shutil.rmtree(abs_dest)
        shutil.move(src_folder, abs_dest)
    else:
        print("Error: Render folder not found on Desktop.")
        # Check if it saved as "Agent_Render_Temp.png" or similar quirks?
        # Listing desktop for debugging if it fails
        
    # Cleanup
    if os.path.exists(script_path):
        os.remove(script_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 render_desktop.py <input.pptx> <output_dir>")
        sys.exit(1)
    render_via_desktop(sys.argv[1], sys.argv[2])
