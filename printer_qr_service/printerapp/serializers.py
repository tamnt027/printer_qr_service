from rest_framework import serializers
from .models import PrinterModel, PrinterTaskModel


class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterModel
        fields = ('id', 'name', 'selected', 'label_size_mm', 'num_label_in_row')


class PrinterTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterTaskModel
        fields = ('id', 'name', 'description', 'created_at', 'updated_at',
                  'status', 'used_rows', 'uuid', 'file_name', 'task_id')
        