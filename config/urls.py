# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from dashboard.views import create_initial_users

urlpatterns = [
    path("admin/", admin.site.urls),

    # Rutas de apps
    path("dashboard/", include("dashboard.urls")),
    path("users/", include("users.urls")),
    path("vcards/", include("vcards.urls")),

    # Raíz: redirige al dashboard del usuario (si no está logueado irá al LOGIN_URL)
    path("", RedirectView.as_view(pattern_name="dashboard:user_home", permanent=False)),

    # 🔴 RUTA TEMPORAL para crear usuarios iniciales en Render
    # NO OLVIDES BORRARLA cuando ya hayas creado y probado los usuarios.
    path("create-users/", create_initial_users, name="create_initial_users"),
]
