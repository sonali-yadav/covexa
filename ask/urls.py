from django.urls import path

from ask import views

app_name = "ask"

urlpatterns = [
    path("", views.page, name="page"),
    path("stream/", views.stream, name="stream"),
    path("policy/", views.policy_answer, name="policy_answer"),
]
