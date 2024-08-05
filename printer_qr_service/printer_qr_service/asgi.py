"""
ASGI config for printer_qr_service project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

import threading

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'printer_qr_service.settings')

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from printerapp.models import PrinterTaskModel, TaskStatusTextChoices

application = get_asgi_application()



# async def relay():
#     source_server = 'ws://source.example/ws/message'  # This is an external server
#     target_server = 'ws://target.example/ws/message'  # This is my Django server
#     async for target in websockets.connect(target_server):
#         try: 
#             async for source in websockets.connect(source_server):
#                 try:    
#                     while True:
#                         try:
#                             message = await source.recv()
#                             await target.send()
#                             # log message
#                         except websockets.ConnectionClosed as e:
#                             # lost source server or target server or both
#                             raise(e) 
#                         except Exception as e:
#                             # did not lose servers
#                             continue
#                 except websockets.ConnectionClosed as e:
#                     # lost source server or target server or both
#                     if target.close_code is not None:
#                         # lost target server and need to start from the outer for loop
#                         # (to get a new target websocket connection)
#                         source.disconnect()       
#                         raise(e)
#                     # lost source server and will continue the inner for loop 
#                     # (to get a new source websocket connection)
#                     continue
#                except Exception as e:
#                     # did not lose any server and will continue the inner for loop 
#                     # (to get a new source websocket connection)
#                     continue
#         except websockets.ConnectionClosed as e:
#             # lost target server and will continue the outer for loop
#             # (to get a new target websocket connection)
#             continue
#         except Exception as e:
#             # did not lose any server and will start the outer for loop   
#             # (to get a new target websocket connection)
#             continue 

# def runWs():
#     asyncio.run(relay())

# import threading
# threading.Thread(target=runWs).start()

def start_pycups_notify() :

    def notify_main():
        
        import cups
        from cups_notify import Subscriber, event
        import time

        def on_event(evt):
            print('New Print Task Event')
            print(evt)
            
            not_completed_tasks = PrinterTaskModel.objects.filter().exclude(status=TaskStatusTextChoices.Completed).all()

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

    if simulator is None or simulator == False:
        threading.Thread(target=notify_main, daemon=True).start()



start_pycups_notify()
