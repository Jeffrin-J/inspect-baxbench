from django.urls import path

from myapp import views

urlpatterns = [
    path("log", views.log),
    path("logs", views.get_logs),
]
