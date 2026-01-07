import zipfile
import os
import shutil
import tempfile

def patch_pptx_content_type(pptx_path):
    print(f"Patching {pptx_path} content types...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract
        with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        # Patch [Content_Types].xml
        ct_path = os.path.join(temp_dir, '[Content_Types].xml')
        if os.path.exists(ct_path):
            with open(ct_path, 'r') as f:
                content = f.read()
            
            # Replace template content type with presentation content type
            new_content = content.replace(
                'application/vnd.openxmlformats-officedocument.presentationml.template.main+xml',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'
            )
            
            if content != new_content:
                print("  Patched [Content_Types].xml")
                with open(ct_path, 'w') as f:
                    f.write(new_content)
            else:
                print("  No template content type found in [Content_Types].xml")
        
        # Re-zip
        # Create a new zip file
        new_pptx_path = pptx_path # Overwrite
        
        # shutil.make_archive defaults to zip and appends .zip, so we need to be careful
        # We manually zip to avoid extension mess
        with zipfile.ZipFile(new_pptx_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
                    
    print(f"Done. {pptx_path} is now a valid PPTX for python-pptx.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fix_potx.py <file.pptx>")
        sys.exit(1)
    
    patch_pptx_content_type(sys.argv[1])
