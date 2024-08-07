"""
WSGI config for printer_qr_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'printer_qr_service.settings')

import rel
import websocket

import threading
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
print("path")
print(dotenv_path)
# Load environment variables from .env file
load_dotenv(dotenv_path)

from printerapp.models import PrinterTaskModel, TaskStatusTextChoices, PrinterModel
from printerapp.serializers import PrinterSerializer

application = get_wsgi_application()

from ..printerapp.pdf_composer import PDFComposer
from ..printerapp.cups import printFile
from ..printerapp.constant import PDF_FOLDER
from uuid import UUID

WS_ACCEPT_CONNECTION = 'WS_ACCEPT_CONNECTION'
WS_PRINTER_ONLINE = 'WS_PRINTER_ONLINE'
WS_PRINT_DATA = 'WS_PRINT_DATA'

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


def start_websocket_to_master():
    def handle_ws_accept_connection(ws :  websocket.WebSocketApp):
        # send WS_PRINTER_ONLINE to master

        selected_printer = PrinterModel.objects.filter(selected=True).first()

        if selected_printer is None:
            print(f"No printer selected to send to master")


        printer_online_obj = {
            'type' : WS_PRINTER_ONLINE,
            'payload': PrinterSerializer(selected_printer).data
        }

        ws.send_text(json.dumps(printer_online_obj))

    def handle_ws_print(ws :  websocket.WebSocketApp, received_obj):
        printer_data = received_obj['payload']
        printer_name = received_obj['printer_name']

        printer_task : PrinterTaskModel
        printer_task = PrinterTaskModel()

        file_name = str(printer_task.uuid) + ".pdf"

        printer_task.file_name = file_name
    

        pdf_composer = PDFComposer(filename=f"{PDF_FOLDER}{file_name}")
        pdf_composer.set_printer_data(printer_data=printer_data)
        pdf_composer.save()

        printer_task.used_rows = pdf_composer.get_used_page()
        printer_task.task_id = printFile(printer=printer_name, printer_task=printer_task)

        printer_task.save()


    def on_message(ws : websocket.WebSocketApp, message : str):
        print(f"On message {message}")
        received_obj = json.loads(message)
        msg_type = received_obj['type']

        if msg_type == WS_ACCEPT_CONNECTION:
            handle_ws_accept_connection(ws)
        elif msg_type == WS_PRINT_DATA:
            handle_ws_print(ws, received_obj)



        pass

    def on_error(ws : websocket.WebSocketApp, error):
        print(f"Websocket connection has error {str(error)}")

    def on_close(ws : websocket.WebSocketApp, close_status_code, close_msg):
        print(f"Closed connected to {ws.url} with code {close_status_code} and message {close_msg}")

    def on_open(ws : websocket.WebSocketApp):
        print(f"Opened connection to {ws.url}")

    ws_address = os.getenv('MASTER_WS_ADDRESS')
    if ws_address is None or ws_address == "":
        print("Warning : Websocket address not set ")
        return
    
    def websocket_main():
        while True:
            try:
                ws = websocket.WebSocketApp(ws_address, on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
                ws.run_forever( reconnect=10)
                print("After run_forever")
            except Exception as e:
                print(f"Websocket error {str(e)}")
            print(f"Reconnect after 10 seconds")
            time.sleep(10)
    
    threading.Thread(target=websocket_main, daemon=True).start()
    




start_pycups_notify()

start_websocket_to_master()

print("Done startup script")
