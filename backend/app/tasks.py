from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import register_events

from .views import fetch_earthquake_data


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(SQLAlchemyJobStore(url='sqlite:///scheduler.sqlite3'), "default")

    # Schedule the fetch_earthquake_data function to run at every minute (00:00, 00:01, 00:02, ...)
    scheduler.add_job(
        fetch_earthquake_data,
        trigger=CronTrigger(second=0),  # Run at the start of every minute
        id="fetch_earthquake_data",  # Unique ID for the job
        replace_existing=True,
        args=[None],  # Pass `None` since the function expects a request object
    )

    register_events(scheduler)
    scheduler.start()
    print("Scheduler started!")