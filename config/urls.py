# config/urls.py
# ======================================================
# Rutas principales del proyecto (root, users, dashboard, vcards)
# y Django Admin movido a /django-admin/ para no chocar con
# el panel admin personalizado del proyecto en /admin/...
# ======================================================

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Redirección raíz → login (users:login)
def root_redirect(request):
    return redirect("users:login")

urlpatterns = [
    # 1) Raíz del sitio
    path("", root_redirect, name="root"),

    # 2) Rutas del dashboard (usuario y admin custom)
    #    Importante: van ANTES que el Django Admin para priorizar /admin/...
    path("", include(("dashboard.urls", "dashboard"), namespace="dashboard")),

    # 3) Auth de usuarios (login/logout)
    path("accounts/", include("users.urls")),

    # 4) Rutas de vCards
    path("vcards/", include(("vcards.urls", "vcards"), namespace="vcards")),

    # 5) Django Admin oficial (movido para evitar conflicto con /admin/...)
    path("django-admin/", admin.site.urls),
    
    path("folders/", include(("folders.urls", "folders"), namespace="folders")),
]
