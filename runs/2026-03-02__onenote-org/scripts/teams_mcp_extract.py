import sys
import os
import time
from playwright.sync_api import sync_playwright

def get_data():
    profile_dir = os.path.abspath("runs/2026-03-02__onenote-org/playwright-profile")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            viewport={"width": 1440, "height": 900}
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Make sure we are in teams
        if "teams.microsoft.com" not in page.url:
            page.goto("https://teams.microsoft.com/v2/")
            time.sleep(10)
        
        print("Looking for the meeting chat...")
        try:
            # Type into the search bar "SC Internal Deal Desk Project Meeting"
            search_box = page.get_by_role("searchbox").first
            search_box.click()
            search_box.fill("SC Internal Deal Desk Project Meeting")
            page.keyboard.press("Enter")
            time.sleep(5)
            
            # Click the result
            result = page.locator("text='SC Internal Deal Desk Project Meeting'").first
            result.click()
            time.sleep(5)
        except Exception as e:
            print("Could not search for the meeting...", e)
            
        print("Looking for the recap tab...")
        try:
            # Try to click recap
            recap_tab = page.get_by_role("tab", name="Recap").first
            if recap_tab.is_visible():
                recap_tab.click()
                time.sleep(3)
        except Exception as e:
            print("Could not find recap tab.", e)

        print("\n\nPlease make sure the 'AI summary' tab is visible, then press Enter here!")
        input("\nPress Enter to extract...> ")

        try:
            ai_summary_text = page.locator("body").inner_text()
            with open("runs/2026-03-02__onenote-org/tmp/teams_ai.txt", "w") as f:
                f.write(ai_summary_text)
            print("Saved AI text.")
        except:
            pass

        print("\n\nPlease go to 'Transcript' tab and scroll down a bit, then press Enter!")
        input("\nPress Enter to extract transcript...> ")

        try:
            t_text = page.locator("body").inner_text()
            with open("runs/2026-03-02__onenote-org/tmp/teams_t.txt", "w") as f:
                f.write(t_text)
            print("Saved Transcript text.")
        except:
            pass
            
        browser.close()

if __name__ == "__main__":
    get_data()
