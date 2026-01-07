import sys
import os
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from shapely.geometry import box
import rtree

def get_shape_bounds(shape):
    """
    Returns (left, bottom, right, top) for shapely box, 
    but PPT uses (left, top, width, height) where y increases downwards.
    Shapely uses Cartesian (y increases upwards).
    To map PPT to Shapely:
    x = left
    y = -top (flip y axis)
    """
    left = shape.left
    top = shape.top
    width = shape.width
    height = shape.height
    
    # Inverted Y axis for cartesian compatibility
    # Bottom in cartesian is -(top + height)
    # Top in cartesian is -top
    return (left, -(top + height), left + width, -top)

def lint_presentation(pptx_path):
    print(f"Linting {pptx_path}...")
    prs = Presentation(pptx_path)
    
    slide_width = prs.slide_width
    slide_height = prs.slide_height
    
    issues = []
    
    for i, slide in enumerate(prs.slides):
        slide_num = i + 1
        print(f"Checking Slide {slide_num}...")
        
        shapes = list(slide.shapes)
        spatial_index = rtree.index.Index()
        shape_geoms = {}
        
        # Pass 1: Build Index
        for idx, shape in enumerate(shapes):
            if shape.rotation != 0:
                # Rotation creates complex polygons, skipping for MVP
                continue
                
            bounds = get_shape_bounds(shape) # (minx, miny, maxx, maxy)
            geom = box(*bounds)
            shape_geoms[idx] = geom
            spatial_index.insert(idx, bounds)
            
            # Check 1: Off-canvas
            # Allow some tolerance?
            slide_box = box(0, -slide_height, slide_width, 0)
            if not slide_box.contains(geom):
                # Tolerance check (floating point)
                if not slide_box.buffer(100).contains(geom):
                    issues.append(f"Slide {slide_num}: Shape '{shape.name}' is partially off-slide.")

        # Pass 2: Check Overlaps
        for idx, shape in enumerate(shapes):
            if idx not in shape_geoms: continue
            
            geom = shape_geoms[idx]
            possible_overlaps = list(spatial_index.intersection(geom.bounds))
            
            for other_idx in possible_overlaps:
                if idx == other_idx: continue
                if other_idx not in shape_geoms: continue
                
                other_geom = shape_geoms[other_idx]
                
                if geom.intersects(other_geom):
                    intersection_area = geom.intersection(other_geom).area
                    min_area = min(geom.area, other_geom.area)
                    
                    # Ignore tiny overlaps (frames touching)
                    if min_area > 0 and (intersection_area / min_area) > 0.05:
                        # 5% overlap threshold
                        other_shape = shapes[other_idx]
                        
                        # Filter out innocuous overlaps?
                        # e.g. Title usually doesn't overlap Body, but sometimes frames touch.
                        # Pictures often overlap backgrounds.
                        
                        # Just reporting for now.
                        issues.append(f"Slide {slide_num}: Overlap detected between '{shape.name}' and '{other_shape.name}'")

    if issues:
        print("\n--- LINT FAILURES DETECTED ---")
        for issue in issues:
            print(f"[FAIL] {issue}")
        print(f"Total Issues: {len(issues)}")
        return False
    else:
        print("\n[PASS] No geometry issues found.")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 lint_slides.py <input.pptx>")
        sys.exit(1)
        
    success = lint_presentation(sys.argv[1])
    sys.exit(0 if success else 1)
