
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .models import PrinterModel, PrinterTaskModel

from .constant import PDF_FOLDER

def get_available_printers() :

    simulator = os.getenv('CUPS_SIMULATOR')

    if simulator is None or simulator == 'False':

        import cups
        conn = cups.Connection ()
        printers = conn.getPrinters ()
        printer_names = list(printers.keys())
    else:
        printer_names = ["Simulator Printer 1",
                        "Simulator Printer 2",
                        "Simulator Printer 3",
                        ]

    return printer_names


def printFile(printer : PrinterModel, printer_task : PrinterTaskModel ):

    simulator = os.getenv('CUPS_SIMULATOR')

    if simulator is None or simulator == 'False':

        import cups
        conn = cups.Connection ()

        file_name = printer_task.file_name

        task_id = conn.printFile(printer.name, f"{PDF_FOLDER}{file_name}", str(printer_task.uuid) , {})
        return task_id
    else:
        import random
        return random.randint(1000, 9000)

