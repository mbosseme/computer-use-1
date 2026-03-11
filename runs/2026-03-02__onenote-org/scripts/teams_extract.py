import sys
from playwright.sync_api import sync_playwright
import os
import time

def main():
    profile_dir = os.path.abspath('runs/2026-03-02__onenote-org/playwright-profile')
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        
        # Check if there are existing pages, otherwise use the first
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("Navigating to Teams...")
        page.goto("https://teams.microsoft.com/v2/")
        
        print("\n" + "="*80)
        print("ACTION REQUIRED:")
        print("1. Log in to Teams if you are not already.")
        print("2. Navigate to the 'SC Internal Deal Desk Project Meeting' recording we were discussing.")
        print("3. Ensure the 'AI summary' tab is visible.")
        print("4. Press Enter here in the terminal when you are ready to extract.")
        print("="*80 + "\n")
        
        input("Press Enter to continue...")
        
        print("\nExtracting AI summary...")
        try:
            page.locator("button:has-text('Expand all')").click(timeout=3000)
            time.sleep(1)
        except Exception:
            print("Expand all button not found or already expanded.")
            pass
            
        print("Capturing AI Summary content...")
        summary_text = ""
        try:
            summary_text = page.locator("body").inner_text()
        except:
            print("Could not grab body inner text.")
            
        print("Switching to Transcript tab...")
        try:
            page.locator("button:has-text('Transcript')").click(timeout=5000)
            time.sleep(2)
            print("Capturing full Transcript content...")
            transcript_text = page.locator("body").inner_text()
        except Exception as e:
            print(f"Failed to click Transcript tab: {e}")
            transcript_text = "ERROR: " + str(e)

        os.makedirs("runs/2026-03-02__onenote-org/tmp", exist_ok=True)
        with open("runs/2026-03-02__onenote-org/tmp/teams_summary_raw.txt", "w") as f:
            f.write(summary_text)
            
        with open("runs/2026-03-02__onenote-org/tmp/teams_transcript_raw.txt", "w") as f:
            f.write(transcript_text)
            
        print("Extraction complete. Saving to tmp. You can close the browser now.")
        time.sleep(2)
        browser.close()

if __name__ == "__main__":
    main()
