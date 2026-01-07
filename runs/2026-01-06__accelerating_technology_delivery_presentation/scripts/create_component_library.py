from pptx import Presentation
import os

# Configuration
RUN_ID = "2026-01-06__accelerating_technology_delivery_presentation"
INPUT_TEMPLATE = f"runs/{RUN_ID}/tmp/Premier_Template_Fixed.pptx"
OUTPUT_LIBRARY = f"runs/{RUN_ID}/assets/Premier_Components.pptx"

def create_library():
    if not os.path.exists(INPUT_TEMPLATE):
        print(f"Error: Template not found at {INPUT_TEMPLATE}")
        return

    prs = Presentation(INPUT_TEMPLATE)
    
    # We will append our component prototypes to the end of the existing deck.
    # We won't try to delete existing slides to avoid corruption issues.
    
    # --- COMPONENT 1: TITLE SLIDE (ID: COMP_TITLE) ---
    # Layout 1: "Premier Title Slide 1 - Dark"
    slide_layout = prs.slide_layouts[1] 
    slide = prs.slides.add_slide(slide_layout)
    
    # Explicitly naming/tagging for the future "Selector" logic
    # (python-pptx doesn't persist arbitrary tags easily visible to user, but we rely on position or content)
    title = slide.placeholders[0]
    subtitle = slide.placeholders[10]
    
    title.text = "{{TITLE}}"
    subtitle.text = "{{SUBTITLE}}"
    
    # --- COMPONENT 2: AGENDA / LIST (ID: COMP_LIST) ---
    # Layout 4: "Premier Main Content 1a" (Title + Content)
    slide_layout = prs.slide_layouts[4]
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.placeholders[0]
    body = slide.shapes.placeholders[10]
    
    title.text = "{{SECTION_TITLE}}"
    body.text = "{{BULLET_LIST}}"
    
    # --- COMPONENT 3: SECTION HEADER (ID: COMP_SECTION) ---
    # Let's find a Section Header layout. 
    # Usually index 2 or similar. Let's inspect quickly or just guess Layout 2 ("Section Header")
    # Based on standard templates. If "Premier" follows standard:
    # 0 = Title
    # 1 = Title and Content
    # 2 = Section Header
    # UNVERIFIED: I'll use Layout 2 for now. If it looks wrong we fix it.
    slide_layout = prs.slide_layouts[2] 
    slide = prs.slides.add_slide(slide_layout)
    
    try:
        title = slide.shapes.placeholders[0]
        title.text = "{{SECTION_HEADER}}"
    except IndexError:
        print("Warning: Layout 2 might not have placeholder 0")

    # Save
    prs.save(OUTPUT_LIBRARY)
    print(f"Library created at {OUTPUT_LIBRARY}")

if __name__ == "__main__":
    create_library()
