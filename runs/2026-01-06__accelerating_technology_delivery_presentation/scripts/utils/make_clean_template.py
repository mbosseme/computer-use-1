from pptx import Presentation
import sys

def make_clean(input_path, output_path):
    print(f"Cleaning {input_path} -> {output_path}")
    prs = Presentation(input_path)
    
    # Nuke all slides
    xml_slides = prs.slides._sldIdLst
    # Clear the list completely
    xml_slides[:] = [] 
    
    prs.save(output_path)
    print("Cleaned.")

if __name__ == "__main__":
    make_clean(sys.argv[1], sys.argv[2])
