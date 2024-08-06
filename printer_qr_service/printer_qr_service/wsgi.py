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


from uuid import UUID

def get_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
        return uuid_obj
    except ValueError:
        return None


def start_pycups_notify() :

    def notify_main():
        
        import cups
        from cups_notify import Subscriber, event
        import time

        def on_event(evt):
            print('===============New Print Task Event=================')
            print(evt)
            print(evt.description)  # Find created,  started, completed.
            print(evt.guid)
            print(evt.title)  # process to identify task title between ()
            s_index = evt.title.find(' (')
            f_index = evt.title.find(') ', max(0, s_index))

            if s_index > -1 and s_index < f_index:  #find valid position
                task_title = evt.title[s_index + 2 : f_index]

                title_uuid = get_valid_uuid(task_title)

                if title_uuid is None : 
                    print(f"Task title '{title_uuid}' is not an uuid")
                    return
                
                printer_task = PrinterTaskModel.objects.filter(uuid=title_uuid).first()

                if printer_task is None: 
                    print(f"Not found printer task with title '{title_uuid}'")
                    return
                    
                created = evt.description.find("created") != -1
                
                if created:
                    printer_task.status = TaskStatusTextChoices.Created
                    printer_task.save()

                started = evt.description.find("started") != -1

                if started:
                    printer_task.status = TaskStatusTextChoices.Progress
                    printer_task.save()

                stopped = evt.description.find("stopped") != -1
                if stopped:
                    printer_task.status = TaskStatusTextChoices.Stopped
                    printer_task.save()

                completed = evt.description.find("completed") != -1

                if completed:
                    printer_task.status = TaskStatusTextChoices.Completed
                    printer_task.save()


        # Create a CUPS connection
        conn = cups.Connection()

        # Create a new subscriber
        sub = Subscriber(conn)

        # Subscribe the callback to all CUPS events
        sub.subscribe(on_event, [event.CUPS_EVT_JOB_CREATED,
                                event.CUPS_EVT_JOB_COMPLETED,
                                event.CUPS_EVT_JOB_STOPPED,
                                event.CUPS_EVT_JOB_STATE_CHANGED
                                ])

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
