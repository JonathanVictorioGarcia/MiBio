# users/views.py
# ==============================
# Vistas de autenticación:
# - Login con redirección por rol
# - Logout por POST
# ==============================

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView


class RoleLoginView(LoginView):
    """
    Login personalizado:
    - Respeta ?next= si venías de una vista protegida
    - Si el usuario es staff o role == "ADMIN" -> dashboard admin
    - Caso contrario -> dashboard usuario
    """
    template_name = "users/login.html"

    def get_success_url(self):
        # 1) Respeta ?next=
        nxt = self.get_redirect_url()
        if nxt:
            return nxt

        # 2) Redirección por rol
        user = self.request.user
        if getattr(user, "is_staff", False) or getattr(user, "role", "") == "ADMIN":
            return reverse_lazy("dashboard:admin_home")
        return reverse_lazy("dashboard:user_dashboard")


def logout_view(request):
    """
    Cierre de sesión:
    - Por seguridad, solo realiza logout en POST
    - En GET redirige al login (sin error 405)
    """
    if request.method == "POST":
        logout(request)
        return redirect(reverse_lazy("users:login"))
    return redirect(reverse_lazy("users:login"))
