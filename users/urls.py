# users/urls.py
# ======================================================
# Rutas de autenticación de la app "users"
# ======================================================

from django.urls import path
from .views import RoleLoginView, logout_view

app_name = "users"

urlpatterns = [
    path("login/",  RoleLoginView.as_view(), name="login"),
    path("logout/", logout_view,            name="logout"),
]
