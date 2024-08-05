from django.urls import path

from .views import PrintRequestView

urlpatterns = [
    path("print", PrintRequestView.as_view(), name="index"),
]