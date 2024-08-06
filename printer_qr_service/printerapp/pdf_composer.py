from reportlab.pdfgen import canvas  
from reportlab.lib.units import mm
from reportlab_qrcode import QRCodeImage
import json

class PDFComposer:
    def __init__(self, filename : str = "sample.pdf", 
                 num_labels_one_line : int = 4,
                label_size_mm = 25, 
                # qr_size_mm = 21,
                qr_border_mm = 1,
                max_title_length = 12,
                ) -> None:
        

        self._filename = filename
        self._num_labels_one_line = num_labels_one_line
        self._label_size_mm = label_size_mm
        self._qr_size_mm = 0.84 * label_size_mm
        self._qr_border_mm = qr_border_mm
        self._max_title_length = max_title_length

        self._pdf = canvas.Canvas(self._filename, bottomup=0) 
        self._pdf.setPageSize((self._num_labels_one_line * label_size_mm * mm, label_size_mm  * mm))



    def draw_border(self):
        self._pdf.rect(0, 0, self._label_size_mm * mm, self._label_size_mm*mm, stroke=1, fill=0)
        self._pdf.rect(self._label_size_mm*mm, 0, self._label_size_mm * mm, self._label_size_mm*mm, stroke=1, fill=0)
        self._pdf.rect(2*self._label_size_mm*mm, 0, self._label_size_mm * mm, self._label_size_mm*mm, stroke=1, fill=0)
        self._pdf.rect(3*self._label_size_mm*mm, 0, self._label_size_mm * mm, self._label_size_mm*mm, stroke=1, fill=0)
        pass



    def draw_qr(self, qr_content : str, title : str, label_offset : int = 0):

        qr = QRCodeImage(qr_content, size=self._qr_size_mm * mm,
                    fill_color='black',
                    back_color='white',
                    border= self._qr_border_mm)
        qr.drawOn(self._pdf, label_offset * self._label_size_mm * mm +  0.08 * self._label_size_mm * mm, 0.5 * mm)

        self._pdf.setFont("Times-Roman", 0.16 * self._label_size_mm * mm) 
        self._pdf.drawString(label_offset * self._label_size_mm * mm + 0.5*mm, 0.96 * self._label_size_mm * mm, title[: self._max_title_length])

    def set_printer_data(self, printer_data):
        label_counter = 0
        for info in printer_data:
            qr_content = info["qr_content"]
            title = info["title"] if 'title' in info else ""
            quantity = info['quantity'] if 'quantity' in info else 1
            description = info['description']  if 'description' in info else None

            if description is None:
                content = json.dumps({
                    "UUID" : qr_content,
                    "Title" : title
                })
            else:
                content = json.dumps({
                    "UUID" : qr_content,
                    "Description" : description,
                    "Title" : title
                })
            



            for i in range(quantity):
                label_offset = label_counter % self._num_labels_one_line
                self.draw_qr(content,title, label_offset)
                label_counter += 1

                if label_counter % self._num_labels_one_line == 0 and label_counter >= self._num_labels_one_line:
                    self._pdf.showPage()

    def get_used_page(self):
        return self._pdf.getPageNumber() - 1


    def save(self):
        self._pdf.save()