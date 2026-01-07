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

# Configuration
RUN_ID = "2026-01-06__accelerating_technology_delivery_presentation"
INPUT_DECK = f"runs/{RUN_ID}/exports/draft_v2_components.pptx" 
OUTPUT_DIR = f"runs/{RUN_ID}/exports/consensus_loop"

def run_loop():
    print("--------------------------------------------------")
    print("STARTING CONSENSUS LOOP (v2.0)")
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
        # GATE 1: GEOMETRY LINTER
        # ------------------------------------------------------------------
        print("\n>>> GATE 1: GEOMETRY LINTER check...")
        try:
            lint_slides.lint_presentation(current_candidate)
            pass_gate_1 = True
            print("Gate 1: PASSED (No Geometry Crashes)")
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
        
        critique_buffer = []
        
        prs = Presentation(current_candidate)
        
        for i, png_path in enumerate(pngs):
            slide_idx = i 
            if slide_idx >= len(prs.slides):
                break
                
            slide = prs.slides[slide_idx]
            print(f"   Analyzing Slide {i+1}...")
            
            # 1. Overlay
            annotated_path = png_path.replace(".png", "_annotated.png")
            out_path, shape_index = qa_vision.draw_overlays(png_path, slide, prs.slide_width, prs.slide_height, output_path=annotated_path)
            
            # 2. Critique
            critique = qa_vision.critique_slide_with_gemini(annotated_path)
            
            if critique:
                print(f"      GEMINI CRITIQUE: \n{critique}")
                critique_buffer.append(f"Slide {i+1}: {critique}")
            else:
                fallback = qa_vision.simple_critique(shape_index)
                print(f"      FALLBACK CHECK: {fallback}")
                critique_buffer.append(f"Slide {i+1}: {fallback}")

        # LOG THE REPORT
        report_path = os.path.join(OUTPUT_DIR, f"report_iter_{iteration}.txt")
        with open(report_path, "w") as f:
            f.write("\n".join(critique_buffer))
            
        print(f"\nReport written to {report_path}")
        print("Consensus loop cycle complete. (Auto-patching paused for MVP review)")
        break 

if __name__ == "__main__":
    run_loop()
