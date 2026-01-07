import sys
import os
import shutil
import time
import glob

# Ensure we can import from utils
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.join(current_dir, 'utils')
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

import lint_slides
import render_slides
import qa_vision
from pptx import Presentation

import json

# Configuration
RUN_ID = "2026-01-06__accelerating_technology_delivery_presentation"
INPUT_DECK = f"runs/{RUN_ID}/exports/draft_v4_content.pptx" 
OUTPUT_DIR = f"runs/{RUN_ID}/exports/consensus_loop_v4"
SHAPE_MAP_PATH = os.path.join(OUTPUT_DIR, "shape_map.json")

def run_loop():
    print("--------------------------------------------------")
    print("STARTING CONSENSUS LOOP (v2.0) - Azure GPT-5.2 Edition")
    print("--------------------------------------------------")
    
    if not os.path.exists(INPUT_DECK):
        print(f"CRITICAL: Input deck not found at {INPUT_DECK}")
        print("Please run generating script first.")
        return

    # CLEANUP: Wipe output directory to ensure fresh renders
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    
    # Create output structure
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Copy input to "current_candidate.pptx"
    current_candidate = os.path.join(OUTPUT_DIR, "candidate.pptx")
    open(current_candidate, 'wb').write(open(INPUT_DECK, 'rb').read())
    
    iteration = 1
    max_iterations = 2 # Keeping it short for demo
    
    pass_gate_1 = False
    pass_gate_2 = False

    while iteration <= max_iterations:
        print(f"\n[ITERATION {iteration}]")
        
        # ------------------------------------------------------------------
        # GATE 1: GEOMETRY LINTER (Now generates Shape Map)
        # ------------------------------------------------------------------
        print("\n>>> GATE 1: GEOMETRY LINTER check...")
        try:
            # We call lint_presentation with the export path
            success = lint_slides.lint_presentation(current_candidate, map_output_path=SHAPE_MAP_PATH)
            if success:
                pass_gate_1 = True
                print("Gate 1: PASSED (No Geometry Crashes)")
            else:
                print("Gate 1: FAILED (Geometry Issues)")
                # In real loop we would retry, here we break or continue to debug
                # break
        except Exception as e:
            print(f"Gate 1: FAILED with exception: {e}")
            break

        # ------------------------------------------------------------------
        # GATE 2: RENDERING & VISUAL CRITIC
        # ------------------------------------------------------------------
        print("\n>>> EXECUTION: Rendering Slides (macOS Native)...")
        render_dir = os.path.join(OUTPUT_DIR, f"render_iter_{iteration}")
        render_slides.render_deck(current_candidate, render_dir)
        
        # Get list of PNGs
        pngs = sorted(glob.glob(os.path.join(render_dir, "*.png")))
        if not pngs:
            print("CRITICAL: No PNGs generated. Rendering failed.")
            break
            
        print(f"\n>>> GATE 2: VISUAL CRITIC (Set-of-Mark Analysis)...")
        
        # Load the shape map
        if not os.path.exists(SHAPE_MAP_PATH):
            print("CRITICAL: Shape Map missing. Cannot perform SoM Analysis.")
            break
            
        with open(SHAPE_MAP_PATH, "r") as f:
            shape_map = json.load(f)
        
        critique_buffer = []
        
        for i, png_path in enumerate(pngs):
            slide_idx = i # 0-based index matching lint_slides output
            
            print(f"   Analyzing Slide {i+1}...")
            
            # Review Slide (Includes Overlay + GPT-5.2 Call)
            critique = qa_vision.review_slide(png_path, shape_map, slide_idx)
            
            if critique:
                print(f"      GPT-5.2 CRITIQUE: \n{critique}")
                critique_buffer.append(f"Slide {i+1}:\n{critique}")
            else:
                critique_buffer.append(f"Slide {i+1}: Critique Skipped/Failed.")

        # LOG THE REPORT
        report_path = os.path.join(OUTPUT_DIR, f"report_iter_{iteration}.txt")
        with open(report_path, "w") as f:
            f.write("\n".join(critique_buffer))
            
        print(f"\nReport written to {report_path}")
        print("Consensus loop cycle complete. (Auto-patching paused for MVP review)")
        break 
 

if __name__ == "__main__":
    run_loop()
