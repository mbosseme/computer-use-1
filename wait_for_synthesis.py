import time
import os
import psutil

print("Waiting for summarize_incremental.py to finish...")
while True:
    running = False
    for p in psutil.process_iter(['cmdline']):
        if p.info['cmdline'] and 'summarize_incremental.py' in ' '.join(p.info['cmdline']):
            running = True
            break
    if not running:
        print("Process finished.")
        break
    time.sleep(10)
