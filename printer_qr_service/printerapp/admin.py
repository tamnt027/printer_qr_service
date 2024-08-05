from django.contrib import admin
from django import forms
from .models import  PrinterModel

from .cups import get_available_printers
# Register your models here.



def get_available_printer_choices():
    available_printer_names = get_available_printers()

    # registed_printers = PrinterModel.objects.all()
    # registed_printer_names = [printer.name for printer in registed_printers ]

    choices = []
    for name in available_printer_names:
        # if name not in registed_printer_names:
        choices.append((name,name))


    return tuple(choices)

class PrinterForm(forms.ModelForm):
    name = forms.ChoiceField(choices=get_available_printer_choices())


# @admin.register(PrinterModel)
class PrinterAdmin(admin.ModelAdmin):
    fields = ('name', 'selected', 'label_size_mm', 'num_label_in_row')
    list_display = ('name', 'selected', 'label_size_mm', 'num_label_in_row')
    form = PrinterForm


admin.site.register(PrinterModel, PrinterAdmin)