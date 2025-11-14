# dashboard/views.py
# ==========================================================
# Vistas del dashboard (admin y usuario).
# Aquí preparamos datos (mock/estáticos por ahora) y renderizamos
# los templates de cada sección del dashboard.
# ==========================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from datetime import date
from calendar import month_abbr

from .auth import staff_required
from .forms import ProfileForm


# ==========================================================
# Helper: validar si el usuario es ADMIN (para vista admin)
# ==========================================================
def is_admin(user):
    """
    Consideramos admin si:
    - Tiene role == "ADMIN"   (modelo con roles), o
    - Es staff, o
    - Es superuser.
    Así evitamos quedarnos fuera si el campo role no está configurado.
    """
    role = getattr(user, "role", "")
    return role == "ADMIN" or user.is_staff or user.is_superuser


# ==========================================================
# VISTA TEMPORAL: crear usuarios iniciales en producción
# ==========================================================
def create_initial_users(request):
    """
    Vista TEMPORAL para crear los usuarios iniciales:

      - Admin / SoyAmin  (superusuario)
      - usuario1 / ContraseñaSegura123  (usuario normal)

    IMPORTANTE: Después de ejecutar esta URL y verificar que puedes
    iniciar sesión, BORRA esta vista y la ruta en config/urls.py.
    """
    User = get_user_model()
    creados = []

    if not User.objects.filter(username="Admin").exists():
        User.objects.create_superuser(
            username="Admin",
            password="SoyAmin",
            email="admin@mibio.com",
        )
        creados.append("Admin")

    if not User.objects.filter(username="usuario1").exists():
        User.objects.create_user(
            username="usuario1",
            password="ContraseñaSegura123",
            email="usuario1@mibio.com",
        )
        creados.append("usuario1")

    if not creados:
        msg = "Los usuarios ya existían. No se creó ninguno nuevo."
    else:
        msg = "Usuarios creados: " + ", ".join(creados)

    return HttpResponse(msg)


# ==========================================================
# Vista: Mejorar plan (Planes, comparación, etc.)
# ==========================================================
def user_upgrade(request):
    """
    Muestra la página de “Mejorar plan”.
    Por ahora la data es MOCK (estática) para la interfaz.
    En un futuro, estos datos deben venir de la base de datos/modelos.
    """

    # Plan actual del usuario (mock)
    current_plan = {
        "name": "Starter",
        "price": 0,
        "period": "mes",
        "badge": "Plan actual",
        "features": [
            "1 tarjeta digital",
            "100 visitas/mes",
            "Estadísticas básicas",
            "Temas básicos",
        ],
        "limits": {"vcards": 1, "views": 100},
    }

    # Planes disponibles (mock)
    plans = [
        {
            "slug": "starter",
            "name": "Starter",
            "price": 0,
            "period": "mes",
            "highlight": False,
            "description": "Perfecto para empezar",
            "features": [
                "1 tarjeta digital",
                "100 visitas/mes",
                "Estadísticas básicas",
                "1 plantilla",
            ],
            "cta": "Continuar con Starter",
        },
        {
            "slug": "pro",
            "name": "Pro",
            "price": 9,
            "period": "mes",
            "highlight": True,  # Este se resalta en la UI
            "description": "Para marcas personales y equipos pequeños",
            "features": [
                "Hasta 10 tarjetas",
                "10,000 visitas/mes",
                "Estadísticas avanzadas",
                "Plantillas premium",
                "Dominio personalizado",
                "Botón WhatsApp + Links ilimitados",
            ],
            "cta": "Mejorar a Pro",
        },
        {
            "slug": "business",
            "name": "Business",
            "price": 29,
            "period": "mes",
            "highlight": False,
            "description": "Para organizaciones y franquicias",
            "features": [
                "Tarjetas ilimitadas",
                "Visitas ilimitadas*",
                "SAML/SSO (empresas)",
                "Gestión multi-equipo",
                "Soporte prioritario",
                "SLA y facturación",
            ],
            "cta": "Contactar ventas",
        },
    ]

    # Tabla comparativa de características (mock)
    comparison = [
        {"feature": "Tarjetas incluidas", "starter": "1", "pro": "10", "business": "Ilimitadas"},
        {"feature": "Visitas/mes", "starter": "100", "pro": "10,000", "business": "Ilimitadas*"},
        {"feature": "Plantillas premium", "starter": "—", "pro": "✔", "business": "✔"},
        {"feature": "Dominio personalizado", "starter": "—", "pro": "✔", "business": "✔"},
        {"feature": "Estadísticas avanzadas", "starter": "—", "pro": "✔", "business": "✔"},
        {"feature": "SAML/SSO", "starter": "—", "pro": "—", "business": "✔"},
        {"feature": "Soporte prioritario", "starter": "—", "pro": "—", "business": "✔"},
    ]

    # Add-ons opcionales (mock)
    addons = [
        {"name": "Dominio .com", "desc": "Conecta o compra tu dominio", "price": 8, "period": "mes"},
        {"name": "QR dinámico", "desc": "QR editable con UTM", "price": 3, "period": "mes"},
        {"name": "Remover marca MiBio", "desc": "White-label en tu tarjeta", "price": 5, "period": "mes"},
    ]

    # Preguntas frecuentes para esta página (mock)
    faqs = [
        {"q": "¿Puedo cambiar de plan cuando quiera?", "a": "Sí, puedes subir o bajar de plan en cualquier momento. El cambio se prorratea automáticamente."},
        {"q": "¿Hay permanencia?", "a": "No. Puedes cancelar en cualquier momento sin penalización."},
        {"q": "¿Ofrecen descuentos anuales?", "a": "Sí, paga anual y ahorra hasta 20% (aplicable a Pro y Business)."},
        {"q": "¿Cómo integro Google Analytics?", "a": "En Pro y Business puedes añadir tu ID de GA4 por tarjeta o a nivel cuenta."},
    ]

    context = {
        "current_plan": current_plan,
        "plans": plans,
        "comparison": comparison,
        "addons": addons,
        "faqs": faqs,
    }
    return render(request, "dashboard/user_upgrade.html", context)


# ==========================================================
# Vista: Soporte (tickets, centro de ayuda, estado del sistema)
# ==========================================================
def user_support(request):
    """
    Página de soporte del usuario.
    Muestra estado del sistema, enlaces rápidos, categorías de ayuda,
    tickets recientes y FAQs. Todo por ahora es MOCK.
    """

    # Estado del sistema (mock)
    system_status = {
        "status": "operational",  # valores posibles: "operational" | "degraded" | "incident"
        "message": "Todos los sistemas operativos",
        "updated_at": "hoy 10:15",
    }

    # Enlaces rápidos (mock)
    quick_links = [
        {"name": "Abrir ticket", "icon": "📝", "href": "#new-ticket", "variant": "primary"},
        {"name": "Centro de ayuda", "icon": "📚", "href": "#help-center", "variant": "ghost"},
        {"name": "WhatsApp", "icon": "💬", "href": "#whatsapp", "variant": "ghost"},
        {"name": "Email", "icon": "✉️", "href": "#email", "variant": "ghost"},
    ]

    # Categorías del centro de ayuda (mock)
    help_categories = [
        {"title": "Tarjetas digitales", "desc": "Creación, diseño, enlaces y QR", "articles": 18},
        {"title": "Planes y Facturación", "desc": "Suscripciones, cupones, recibos", "articles": 12},
        {"title": "Estadísticas", "desc": "Métricas, GA4, privacidad", "articles": 9},
        {"title": "Integraciones", "desc": "GA4, Meta Pixel, Zapier", "articles": 14},
        {"title": "Cuenta y Seguridad", "desc": "Acceso, 2FA, roles", "articles": 11},
        {"title": "Problemas comunes", "desc": "Errores frecuentes y fixes", "articles": 22},
    ]

    # Tickets recientes del usuario (mock)
    recent_tickets = [
        {"id": "#3241", "subject": "No carga la previsualización", "status": "Abierto", "updated": "ayer 16:20"},
        {"id": "#3238", "subject": "Error al subir imagen", "status": "En progreso", "updated": "ayer 10:41"},
        {"id": "#3210", "subject": "Cambio de plan a Pro", "status": "Resuelto", "updated": "hace 3 días"},
    ]

    # FAQs (mock)
    faqs = [
        {"q": "¿Cómo creo y comparto mi tarjeta?", "a": "Desde “Mis tarjetas” crea una nueva, personaliza y comparte el enlace o QR."},
        {"q": "¿Puedo conectar Google Analytics?", "a": "Sí, en Pro/Business puedes añadir tu ID de GA4 por tarjeta o a nivel cuenta."},
        {"q": "¿Cómo cambio o cancelo mi plan?", "a": "Ve a “Mejorar plan”. No hay permanencia; el cambio se prorratea."},
        {"q": "¿Dónde descargo mis facturas?", "a": "En la misma sección de plan, encontrarás el historial de facturación."},
    ]

    context = {
        "system_status": system_status,
        "quick_links": quick_links,
        "help_categories": help_categories,
        "recent_tickets": recent_tickets,
        "faqs": faqs,
        "support_hours": "Lun–Vie 9:00–18:00 (CDMX)",
        "sla_note": "Tiempo medio de primera respuesta: 2–4 h hábiles (Pro/Business prioritario).",
    }
    return render(request, "dashboard/user_support.html", context)


# ==========================================================
# Vista: Home del admin (sólo para usuarios con rol ADMIN)
# ==========================================================
@login_required
@user_passes_test(is_admin)  # Solo usuarios con role == "ADMIN"
def admin_home(request):
    # KPIs mock
    kpis = [
        {"label": "Usuarios activos", "value": "1,284", "delta": 8.2, "note": "vs mes anterior"},
        {"label": "Tarjetas publicadas", "value": "3,920", "delta": 3.1, "note": "total"},
        {"label": "Ingresos (MXN)", "value": "$78,450", "delta": 5.6, "note": "últimos 30 días"},
        {"label": "Tickets abiertos", "value": "12", "delta": -10.5, "note": "variación"},
    ]
    # Serie mensual mock (últimos 12 meses)
    months = []
    users_series = []
    for i in range(11, -1, -1):
        m = (date.today().month - i - 1) % 12 + 1
        months.append(month_abbr[m])
        users_series.append(120 + (i * 7) % 60)  # mock simple

    # Distribución de planes mock
    plans_data = [52, 33, 15]

    # Actividad mock
    activity = [
        {"date": "2025-10-26 18:42", "user": "ana@demo.com", "action": "Alta", "entity": "Usuario", "detail": "Se registró en plan Básico"},
        {"date": "2025-10-26 16:03", "user": "carlos@demo.com", "action": "Upgrade", "entity": "Plan", "detail": "Básico → Pro"},
        {"date": "2025-10-25 13:11", "user": "ventas@empresa.com", "action": "Publicación", "entity": "Tarjeta", "detail": "/coco-playa"},
        {"date": "2025-10-24 09:58", "user": "soporte@mibio.live", "action": "Cierre", "entity": "Ticket", "detail": "#1024 cerrado"},
    ]

    ctx = {
        "kpis": kpis,
        "months": months,
        "users_series": users_series,
        "plans_data": plans_data,
        "activity": activity,
    }
    return render(request, "admin/admin_home.html", ctx)


def admin_users(request):
    return render(request, "admin/admin_users.html")


def admin_vcards(request):
    return render(request, "admin/admin_vcards.html")


def admin_plans(request):
    return render(request, "admin/admin_plans.html")


def admin_support(request):
    return render(request, "admin/admin_support.html")


def admin_settings(request):
    return render(request, "admin/admin_settings.html")


# ==========================================================
# Vista: Home del usuario (requiere login)
# ==========================================================
@login_required
def user_home(request):
    # Renderiza el panel principal del usuario
    return render(request, "dashboard/user_home.html")


# ==========================================================
# Vista: Editar perfil (requiere login)
# ==========================================================
@login_required
def edit_profile(request):
    """
    Editar datos del perfil del usuario autenticado.
    GET  -> muestra formulario con los datos actuales.
    POST -> valida y guarda cambios; muestra mensajes de éxito/error.
    """
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos se han actualizado correctamente.")
            return redirect("dashboard:edit_profile")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "dashboard/edit_profile.html", {"form": form})


# ==========================================================
# Vista: Crear tarjeta (editor) (requiere login)
# ==========================================================
@login_required
def user_vcard_create(request):
    """
    Página de 'Crear Tarjeta' integrada al dashboard del usuario.
    Por ahora sólo renderiza la UI. La lógica HTMX/preview se maneja
    desde la app 'vcards' (endpoints /vcards/preview/ y uploads).
    """
    return render(request, "dashboard/user_vcard_create.html")


# ==========================================================
# Vista: Listado de tarjetas (requiere login)
# ==========================================================
@login_required
def user_vcards_list(request):
    """
    Vista 'Mis tarjetas'.
    Por ahora es la interfaz (mock). En el futuro, cargar desde la BD
    las vCards del usuario autenticado.
    """
    return render(request, "dashboard/user_vcards_list.html")


# ==========================================================
# Vista: Estadísticas (requiere login)
# ==========================================================
@login_required
def user_stats(request):
    # Sólo render de la página de estadísticas (la UI usa Chart.js con datos demo).
    return render(request, "dashboard/user_stats.html")


# ==========================================================
# Vista: Tutoriales (requiere login)
# ==========================================================
@login_required
def user_tutorials(request):
    """
    Muestra una galería/listado de videotutoriales.
    Los datos son de ejemplo (mock). 'source' puede ser 'youtube' o 'mp4'.
    """
    tutorials = [
        {
            "id": "t1",
            "title": "Primeros pasos en Mibio",
            "duration": "06:42",
            "level": "Básico",
            "category": "General",
            "thumb": "https://images.unsplash.com/photo-1522199710521-72d69614c702?q=80&w=1200&auto=format&fit=crop",
            "source": "youtube",
            "youtube_id": "dQw4w9WgXcQ",
            "desc": "Tour rápido por el panel y cómo navegar.",
        },
        {
            "id": "t2",
            "title": "Crear tu primera tarjeta",
            "duration": "10:15",
            "level": "Básico",
            "category": "Tarjetas",
            "thumb": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?q=80&w=1200&auto=format&fit=crop",
            "source": "youtube",
            "youtube_id": "ysz5S6PUM-U",
            "desc": "Desde plantilla hasta compartir con QR.",
        },
        {
            "id": "t3",
            "title": "Carpetas y organización",
            "duration": "07:28",
            "level": "Intermedio",
            "category": "Organización",
            "thumb": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=1200&auto=format&fit=crop",
            "source": "mp4",
            "mp4": "https://filesamples.com/samples/video/mp4/sample_640x360.mp4",
            "desc": "Mejores prácticas para equipos.",
        },
        {
            "id": "t4",
            "title": "Estadísticas y GA4",
            "duration": "09:03",
            "level": "Intermedio",
            "category": "Estadísticas",
            "thumb": "https://images.unsplash.com/photo-1551281044-8d8d0d8c8c02?q=80&w=1200&auto=format&fit=crop",
            "source": "youtube",
            "youtube_id": "rUWxSEwctFU",
            "desc": "Lee métricas y conecta Google Analytics.",
        },
        {
            "id": "t5",
            "title": "Diseño y branding",
            "duration": "12:47",
            "level": "Avanzado",
            "category": "Diseño",
            "thumb": "https://images.unsplash.com/photo-1520975922284-71a0d52b3e51?q=80&w=1200&auto=format&fit=crop",
            "source": "mp4",
            "mp4": "https://filesamples.com/samples/video/mp4/sample_960x400_ocean_with_audio.mp4",
            "desc": "Paleta, tipografías y componentes.",
        },
    ]
    categories = ["General", "Tarjetas", "Organización", "Estadísticas", "Diseño"]
    levels = ["Básico", "Intermedio", "Avanzado"]

    return render(
        request,
        "dashboard/user_tutorials.html",
        {
            "tutorials": tutorials,
            "categories": categories,
            "levels": levels,
        },
    )


# ==========================================================
# Vista: Preguntas Frecuentes (requiere login)
# ==========================================================
@login_required
def user_faqs(request):
    """
    Página de FAQ (Preguntas Frecuentes).
    Muestra categorías, una lista de preguntas y chips de búsqueda rápida.
    Todo mock por ahora.
    """

    categories = [
        "Cuenta y acceso",
        "Tarjetas digitales",
        "Diseño y branding",
        "Estadísticas y privacidad",
        "Planes y facturación",
        "Integraciones",
        "Seguridad y cumplimiento",
        "Soporte y operaciones",
    ]

    faqs = [
        # Cuenta y acceso
        {
            "category": "Cuenta y acceso",
            "q": "¿Olvidé mi contraseña, cómo la restablezco?",
            "a": "Ve a la pantalla de acceso y haz clic en “¿Olvidaste tu contraseña?”. Recibirás un correo con un enlace para crear una nueva.",
        },
        {
            "category": "Cuenta y acceso",
            "q": "¿Puedo activar 2FA (autenticación en dos pasos)?",
            "a": "Sí. En Ajustes › Seguridad puedes activar 2FA con aplicación de autenticación (TOTP).",
        },
        # Tarjetas digitales
        {
            "category": "Tarjetas digitales",
            "q": "¿Cómo creo mi primera tarjeta?",
            "a": "Desde “Crear tarjeta” elige una plantilla, personaliza tus datos y colores. Guarda y comparte con enlace o QR.",
        },
        {
            "category": "Tarjetas digitales",
            "q": "¿Puedo tener varias tarjetas?",
            "a": "Según tu plan. Starter permite 1, Pro hasta 10 y Business ilimitadas.",
        },
        # Diseño y branding
        {
            "category": "Diseño y branding",
            "q": "¿Cómo subo mi logo, banner o video?",
            "a": "En el editor de tarjeta (Perfil) tienes tiles para subir imágenes o video. Aceptamos JPG/PNG y MP4 cortos.",
        },
        {
            "category": "Diseño y branding",
            "q": "¿Puedo usar mi dominio propio?",
            "a": "Sí, en Pro/Business puedes conectar un dominio o subdominio desde Ajustes › Dominios.",
        },
        # Estadísticas y privacidad
        {
            "category": "Estadísticas y privacidad",
            "q": "¿Qué métricas ofrece Mibio?",
            "a": "Vistas, origen del tráfico, dispositivos, escaneos de QR y clics en botones/links. Puedes exportar CSV.",
        },
        {
            "category": "Estadísticas y privacidad",
            "q": "¿Puedo integrar GA4?",
            "a": "Sí, añade tu ID de GA4 en Ajustes o por tarjeta (planes Pro/Business).",
        },
        # Planes y facturación
        {
            "category": "Planes y facturación",
            "q": "¿Cómo cambio o cancelo mi plan?",
            "a": "Desde “Mejorar plan” puedes subir/bajar de plan o cancelar sin permanencia. El cambio se prorratea.",
        },
        {
            "category": "Planes y facturación",
            "q": "¿Emiten facturas?",
            "a": "Sí. Descarga tus comprobantes en el historial de facturación una vez aplicado el pago.",
        },
        # Integraciones
        {
            "category": "Integraciones",
            "q": "¿Qué integraciones están disponibles?",
            "a": "GA4, Meta Pixel, Zapier y webhooks. Pronto: HubSpot y Notion (beta).",
        },
        # Seguridad y cumplimiento
        {
            "category": "Seguridad y cumplimiento",
            "q": "¿Cómo protegen mis datos?",
            "a": "Ciframos en tránsito (TLS 1.2+) y aplicamos buenas prácticas de seguridad. Políticas de privacidad y retención vigentes.",
        },
        # Soporte y operaciones
        {
            "category": "Soporte y operaciones",
            "q": "¿En qué horario brindan soporte?",
            "a": "Lun–Vie 9:00–18:00 (CDMX). Pro/Business tienen prioridad de respuesta.",
        },
    ]

    quick_suggestions = ["QR", "GA4", "dominio", "plantillas", "exportar CSV", "2FA", "Zapier", "privacidad"]

    return render(
        request,
        "dashboard/user_faqs.html",
        {
            "categories": categories,
            "faqs": faqs,
            "quick_suggestions": quick_suggestions,
            "active_item": "faqs",
        },
    )
