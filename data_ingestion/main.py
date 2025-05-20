import datetime
import logging
import sys
import time
import signal

from apscheduler.schedulers.background import BackgroundScheduler

from fetch_earthquake import update_new_data

UPDATE_INTERVAL = 10
DEBUG_MODE = True

logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    # Docker logs already include timestamp
    format="%(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    scheduler.add_job(update_new_data, 'interval',
                      seconds=UPDATE_INTERVAL, next_run_time=datetime.datetime.now())

    scheduler.start()

    try:
        while True:
            time.sleep(15)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
