from django.urls import path

from . import views

app_name = "ask"

urlpatterns = [
    path("", views.page, name="page"),
    path("stream/", views.stream, name="stream"),
]
