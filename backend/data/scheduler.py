import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import schedule
import time
from backend.api import fetch_and_store_aqi_for_all_countries

def start_scheduler():
    '''
    This function starts an automatic request of capitals by period.
    The requests are every 15 minutes.
    '''
    def job():
        print("Starting automatic request for aqi-values ...")
        fetch_and_store_aqi_for_all_countries()

    schedule.every().hour.at(":00").do(job) # == 15:00 for example
    schedule.every().hour.at(":15").do(job) # == 15:15
    schedule.every().hour.at(":30").do(job) # == 15:30
    schedule.every().hour.at(":45").do(job) # == 15:45

    print("Scheduler is running. Click Strg+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)
