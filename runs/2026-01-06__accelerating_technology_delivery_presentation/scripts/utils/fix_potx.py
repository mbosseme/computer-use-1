import zipfile
import shutil
import os

def convert_potx_to_pptx_content_type(potx_path, output_pptx_path):
    """
    Workaround for python-pptx rejection of .potx files.
    This function modifies the [Content_Types].xml inside the package
    to look like a regular .pptx presentation.
    """
    
    # 1. Copy file to new location
    shutil.copyfile(potx_path, output_pptx_path)
    
    # 2. We need to replace the content type string inside [Content_Types].xml
    # from: application/vnd.openxmlformats-officedocument.presentationml.template.main+xml
    # to:   application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml
    
    # Since zipfile is read-only or append, we have to rebuild the zip or use a temp dir.
    # Easiest way is to read all files, modify the one we need, and write back to a new zip.
    
    temp_zip_path = output_pptx_path + ".tmp"
    
    with zipfile.ZipFile(output_pptx_path, 'r') as zin:
        with zipfile.ZipFile(temp_zip_path, 'w') as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                
                if item.filename == '[Content_Types].xml':
                    data = data.replace(
                        b'application/vnd.openxmlformats-officedocument.presentationml.template.main+xml',
                        b'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'
                    )
                
                zout.writestr(item, data)
                
    # Move temp zip back to output path
    shutil.move(temp_zip_path, output_pptx_path)
    print(f"Converted template content type: {output_pptx_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 fix_potx.py <input.potx> <output.pptx>")
    else:
        convert_potx_to_pptx_content_type(sys.argv[1], sys.argv[2])
