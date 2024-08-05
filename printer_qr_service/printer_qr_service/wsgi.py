"""
WSGI config for printer_qr_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'printer_qr_service.settings')

import threading
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
print("path")
print(dotenv_path)
# Load environment variables from .env file
load_dotenv(dotenv_path)

from printerapp.models import PrinterTaskModel, TaskStatusTextChoices

application = get_wsgi_application()


def start_pycups_notify() :

    def notify_main():
        
        import cups
        from cups_notify import Subscriber, event
        import time

        def on_event(evt):
            print('===============New Print Task Event=================')
            print(evt)
            
            not_completed_tasks = PrinterTaskModel.objects.filter().exclude(status=TaskStatusTextChoices.Completed).all()
            conn = cups.Connection()
            for task in not_completed_tasks :
                rss = conn.getJobAttributes(task.task_id)
                print(rss)
            

        # Create a CUPS connection
        conn = cups.Connection()

        # Create a new subscriber
        sub = Subscriber(conn)

        # Subscribe the callback to all CUPS events
        sub.subscribe(on_event, [event.CUPS_EVT_JOB_CREATED,
                                event.CUPS_EVT_JOB_COMPLETED,
                                event.CUPS_EVT_JOB_STOPPED,
                                event.CUPS_EVT_JOB_STATE_CHANGED])

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            sub.unsubscribe_all()


    simulator = os.getenv('CUPS_SIMULATOR')

    print(simulator)

    if simulator is None or simulator == 'False':
        threading.Thread(target=notify_main, daemon=True).start()



start_pycups_notify()
