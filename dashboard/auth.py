# dashboard/auth.py
from django.contrib.auth.decorators import user_passes_test, login_required

def staff_required(function=None, login_url='login'):
    """
    Requiere usuario autenticado y con is_staff=True.
    - Si no está autenticado -> redirige a LOGIN_URL
    - Si está autenticado pero no es staff -> 403
    """
    actual_decorator = login_required(
        user_passes_test(lambda u: u.is_staff, login_url=login_url)
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
