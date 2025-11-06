# dashboard/urls.py
# ==========================================================
# Rutas del módulo "dashboard":
# - Panel admin custom (/admin/...)
# - Panel usuario (/user-dashboard/, etc.)
# ==========================================================

from django.urls import path, include
from . import views


app_name = "dashboard"

urlpatterns = [
    # =========================
    # Panel del administrador (custom)
    # =========================
    path("admin-dashboard/", views.admin_home,   name="admin_home"),
    path("admin/usuarios/",  views.admin_users,  name="admin_users"),
    path("admin/tarjetas/",  views.admin_vcards, name="admin_vcards"),
    path("admin/planes/",    views.admin_plans,  name="admin_plans"),
    path("admin/soporte/",   views.admin_support,name="admin_support"),
    path("admin/ajustes/",   views.admin_settings,name="admin_settings"),

    # =========================
    # Panel del usuario
    # =========================
    path("user-dashboard/", views.user_home, name="user_dashboard"),  # nombre “oficial”
    path("user-dashboard/", views.user_home, name="user_home"),       # 👈 alias restaurado

    # =========================
    # Otras secciones del dashboard (usuario)
    # =========================
    path("editar-datos/",    views.edit_profile,      name="edit_profile"),
    path("tarjetas/crear/",  views.user_vcard_create, name="user_vcard_create"),
    path("tarjetas/",        views.user_vcards_list,  name="user_vcards_list"),
    path("estadisticas/",    views.user_stats,        name="user_stats"),
    path("mejorar-plan/",    views.user_upgrade,      name="user_upgrade"),
    path("soporte/",         views.user_support,      name="user_support"),
    path("tutoriales/",      views.user_tutorials,    name="user_tutorials"),
    path("preguntas-frecuentes/", views.user_faqs,    name="user_faqs"),
    
    path("folders/", include(("folders.urls", "folders"), namespace="folders")),
]
