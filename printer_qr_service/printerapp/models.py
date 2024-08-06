from django.db import models
import uuid 

# Create your models here.

class TaskStatusTextChoices(models.TextChoices):
    Initial = "Initial"
    Created= "Created"
    Completed = 'Completed'
    Progress = "Progress"
    Stopped = "Stopped"


class PrinterModel(models.Model):
    name = models.CharField(max_length=200, unique=True )
    selected = models.BooleanField(default=False)
    label_size_mm = models.FloatField(default=25)
    num_label_in_row = models.IntegerField(default=4)

    def __str__(self) -> str:
        return self.name



class PrinterTaskModel(models.Model):
    name = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(choices = TaskStatusTextChoices.choices, default=  TaskStatusTextChoices.Initial, max_length=20,
                                             help_text="Printer task status")
    used_rows = models.IntegerField(default=0)  # how many rows of label this task consumed

    uuid = models.UUIDField( 
         default = uuid.uuid4, 
         editable = False) 

    file_name = models.CharField(max_length=250, blank=True)

    task_id = models.IntegerField(null=True)


    def __str__(self) -> str:
        return self.name

