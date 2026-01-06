from pptx import Presentation
import sys

def inspect_template(template_path):
    print(f"Inspecting: {template_path}")
    prs = Presentation(template_path)
    
    print(f"Total layouts: {len(prs.slide_layouts)}")
    
    for i, layout in enumerate(prs.slide_layouts):
        print(f"\nLayout {i}: {layout.name}")
        for shape in layout.placeholders:
            print(f" - Placeholder idx={shape.placeholder_format.idx}, type={shape.placeholder_format.type}, name='{shape.name}'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspect_template(sys.argv[1])
    else:
        print("Usage: python3 inspect_layouts.py <pptx_path>")
