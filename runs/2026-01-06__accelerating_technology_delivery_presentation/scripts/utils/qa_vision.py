import os
import sys
import json
import base64
from PIL import Image, ImageDraw, ImageFont

# Add local scripts path to allow importing azure_client
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from azure_client import AzureOpenAIResponsesClient
except ImportError:
    # If running from root, path might be different
    sys.path.append(os.path.join(os.getcwd(), "runs/2026-01-06__accelerating_technology_delivery_presentation/scripts/utils"))
    from azure_client import AzureOpenAIResponsesClient

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def draw_overlays(image_path, shape_map, slide_index, output_path):
    """
    Draws Set-of-Mark (SoM) bounding boxes on the image.
    shape_map: dict of slide_idx (int or str) -> list of shape dicts
    slide_index: 0-based index of the slide to process
    """
    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img, "RGBA")
            
            # Load default font
            try:
                # Try to load a generic font (macOS)
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            except IOError:
                font = ImageFont.load_default()

            # Handle string vs int keys in JSON
            shapes = shape_map.get(str(slide_index)) or shape_map.get(slide_index)
            
            if not shapes:
                print(f"No shapes found for slide index {slide_index}")
                return None
            
            img_width, img_height = img.size
            
            for shape in shapes:
                # shape['bbox'] is [left, top, width, height] in 0-1000 normalized space
                norm_box = shape['bbox']
                
                x = (norm_box[0] / 1000) * img_width
                y = (norm_box[1] / 1000) * img_height
                w = (norm_box[2] / 1000) * img_width
                h = (norm_box[3] / 1000) * img_height
                
                sid = shape['id']
                
                # Draw Box (Red, semi-transparent)
                draw.rectangle([x, y, x+w, y+h], outline=(255, 0, 0, 255), width=3)
                draw.rectangle([x, y, x+w, y+h], fill=(255, 0, 0, 20)) 
                
                # Draw Label (ID)
                text = str(sid)
                
                # Draw text background
                text_bbox = draw.textbbox((x, y), text, font=font)
                draw.rectangle(text_bbox, fill=(255, 255, 255, 200))
                draw.text((x, y), text, fill=(255, 0, 0, 255), font=font)

            img.save(output_path)
            # print(f"Saved annotated image to {output_path}")
            return output_path
            
    except Exception as e:
        print(f"Error drawing overlays: {e}")
        return None

def review_slide(image_path, shape_map, slide_index):
    """
    Sends the SOM image to Azure OpenAI GPT-5.2 for critique.
    """
    print(f"Starting review for {image_path}...")
    
    # 1. Overlay
    marked_image_path = image_path.replace(".png", "_annotated.png")
    result_path = draw_overlays(image_path, shape_map, slide_index, marked_image_path)
    
    if not result_path:
        print("Failed to annotate image. Shapes might be missing or image invalid.")
        return None

    # 2. Prepare Client
    try:
        client = AzureOpenAIResponsesClient()
    except ValueError as e:
        print(f"Skipping AI Review: Missing Configuration ({e})")
        return None
    except Exception as e:
        print(f"Skipping AI Review: {e}")
        return None

    # 3. Construct Payload
    base64_image = encode_image(marked_image_path)
    
    system_prompt = """
    You are a Senior Presentation Designer used to strict quality control.
    Your task is to critique a PowerPoint slide render.
    The image provided has "Set-of-Mark" overlays (Red Boxes with IDs).
    
    Identify:
    1. Overlapping text/shapes (COLLISION).
    2. Text that is cut off or off-slide (OVERFLOW).
    3. Empty placeholders that should have content (MISSING).
    4. Poor alignment or "Black on Black" visibility issues.
    
    Return your feedback as a simple bulleted list referencing the visual IDs.
    If the slide looks good, reply "PASS".
    """
    
    user_message = [
        {"type": "text", "text": "Please review this slide for visual defects."},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        }
    ]
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    print(f"Sending request to Azure OpenAI GPT-5.2...")
    try:
        response = client.chat(messages, reasoning_effort="medium")
        print("\n--- GPT-5.2 Critique ---")
        print(response)
        return response
    except Exception as e:
        print(f"GPT-5.2 Call Failed: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python qa_vision.py <image_path> <shape_map.json> [slide_index]")
        sys.exit(1)
        
    img_path = sys.argv[1]
    map_path = sys.argv[2]
    slide_idx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    
    with open(map_path, "r") as f:
        shape_info = json.load(f)
        
    review_slide(img_path, shape_info, slide_idx)
