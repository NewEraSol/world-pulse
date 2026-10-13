"""
Autonomny zberac RSS feedov beziaci v nekonecnom cykle (kazdych 15 minut) pod PM2 na Hetzneri.
"""
import time
import datetime
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from collector import collect_all

def main():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] RSS Daemon na Hetzneri spustený (cyklus 2 minúty)...")
    while True:
        try:
            print(f"\n--- [{datetime.datetime.now().strftime('%H:%M:%S')}] Spúšťam zber najnovších správ ---")
            asyncio.run(collect_all())
        except Exception as e:
            print("Chyba v cykle zberu:", e)
        
        # Pockaj 15 minut (900 sekund)
        time.sleep(120)

if __name__ == '__main__':
    main()
