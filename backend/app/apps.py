import os
import sys
from threading import current_thread

from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Only start the scheduler when running the server, in the main thread, and not in the autoreloader
        if 'runserver' in sys.argv and current_thread().name == 'MainThread' and os.environ.get('RUN_MAIN') == 'true':
            from .tasks import start_scheduler
            start_scheduler()