import datetime
import sys
import time
import signal

from apscheduler.schedulers.background import BackgroundScheduler

from fetch_earthquake import update_new_data

UPDATE_INTERVAL = 10


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
