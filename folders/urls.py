from django.urls import path
from . import views

app_name = "folders"

urlpatterns = [
    path("chips/", views.folders_chips, name="chips"),
    path("save/",  views.folder_save,   name="save"),
    path("delete/", views.folder_delete, name="delete"),
    path("options/", views.folders_options, name="options"),
]
