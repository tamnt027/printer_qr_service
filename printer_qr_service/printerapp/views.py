from django.shortcuts import render
from jsonschema import validate , ValidationError
from rest_framework import views
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from .pdf_composer import PDFComposer
from .models import PrinterModel, PrinterTaskModel

from .serializers import PrinterTaskSerializer

from .constant import PDF_FOLDER

from .myexception import ViewException

from .cups import printFile

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)

schema = {
    "type" : "array",
    "items" : {
        "type" : "object",
        "properties" : {
            "qr_content": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "quantity": {"type": "number"},
        },
        "required": ["qr_content"]
    }
}



class PrintRequestView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # sid = transaction.savepoint()
            payload = request.data

            printer_data = payload['printerData'] if 'printerData' in payload else None

            if printer_data is None:
                raise ViewException("There no printer data")
            
            validate(instance=printer_data, schema=schema)

            if len(printer_data) == 0 :
                raise ViewException("Printer data is empty")

            printer = PrinterModel.objects.filter(selected=True).first()

            if printer is None:
                raise ViewException("No printer selection")

            printer_task : PrinterTaskModel
            printer_task = PrinterTaskModel()

            file_name = str(printer_task.uuid) + ".pdf"

            printer_task.file_name = file_name
        

            pdf_composer = PDFComposer(filename=f"{PDF_FOLDER}{file_name}")
            pdf_composer.set_printer_data(printer_data=printer_data)
            pdf_composer.save()

            printer_task.used_rows = pdf_composer.get_used_page()
            printer_task.task_id = printFile(printer=printer, printer_task=printer_task)

            printer_task.save()
 
            # # transaction.savepoint_commit(sid)
            return Response({
                "status" : "success",
                "payload" : PrinterTaskSerializer(printer_task).data
            }, status=HTTP_200_OK)
        
        except ValidationError as validation_error:
            return Response("Printer Data's Schema is not valid", status=HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)
            # transaction.savepoint_rollback(sid)
            return Response("Bad request", status=HTTP_400_BAD_REQUEST)



