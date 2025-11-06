from django.urls import path
from . import views

app_name = "vcards"

urlpatterns = [
    path("create/", views.create_vcard, name="create"),
    path("preview/", views.preview, name="preview"),
    # NUEVO: validación de slug
    path("check-slug/", views.check_slug, name="check_slug"),
    path("set-global/", views.set_global, name="set_global"),
]
