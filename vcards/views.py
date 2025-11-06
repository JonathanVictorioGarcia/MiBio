# vcards/views.py
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseBadRequest,
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.template.loader import render_to_string
import re

# Intentamos importar el modelo. Si aún no existe, seguimos sin romper.
try:
    from .models import VCard  # ajusta si tu modelo se llama distinto
except Exception:  # pragma: no cover
    VCard = None


# -------------------- Util: flags globales en sesión --------------------
def _get_globals(request):
    """
    Devuelve un dict con los flags 'globales' guardados en sesión, p.ej.:
      { "assets": True, "name": False, "title": True }
    """
    g = request.session.get("vc_global", {})
    # normaliza a bool
    for k, v in list(g.items()):
        g[k] = bool(v)
    return g


# ------------------------------ Vistas UI -------------------------------
@login_required
def create_vcard(request):
    """
    Renderiza el editor (form + preview a la derecha).
    El HTML del editor usa HTMX para mandar POST a /vcards/preview/
    y actualizar el #preview en vivo.
    """
    ctx = {
        "globals": _get_globals(request),
    }
    return render(request, "vcards/create.html", ctx)


@login_required
def preview(request):
    """
    Recibe los valores del formulario (POST) y devuelve SOLO el HTML
    interno para el contenedor #preview (fragmento).
    """
    if request.method != "POST":
        return HttpResponseBadRequest("HTMX preview only accepts POST")

    # Lee valores del form (con defaults para no romper)
    template = request.POST.get("template", "buro")
    full_name = request.POST.get("full_name", "").strip() or "Nombre Apellido"
    job_title = request.POST.get("job_title", "").strip() or "Profesión / Puesto"

    # Colores (con defaults)
    theme_primary = request.POST.get("theme_primary", "#517AFA")
    theme_secondary = request.POST.get("theme_secondary", "#C5FEFF")
    profile_text_primary = request.POST.get("profile_text_primary", "#061244")
    profile_text_secondary = request.POST.get("profile_text_secondary", "#76839B")
    text_primary = request.POST.get("text_primary", "#061244")
    text_secondary = request.POST.get("text_secondary", "#76839B")
    card_bg = request.POST.get("card_bg", "#0D1626")
    block_bg = request.POST.get("block_bg", "#111827")

    # Assets
    photo = request.POST.get("photo", "")
    banner = request.POST.get("banner", "")
    video_url = request.POST.get("video_url", "")

    # Secciones simples
    section_title = request.POST.get("section_title", "Acerca de")
    section_desc = request.POST.get(
        "section_desc", "Escribe una breve descripción para tu vCard."
    )

    # Contactos
    contact_labels = request.POST.getlist("contact_label[]")
    contact_values = request.POST.getlist("contact_value[]")
    contact_types = request.POST.getlist("contact_type[]")
    contacts = []
    for i in range(max(len(contact_labels), len(contact_values), len(contact_types))):
        contacts.append(
            {
                "label": (contact_labels[i] if i < len(contact_labels) else "").strip(),
                "value": (contact_values[i] if i < len(contact_values) else "").strip(),
                "type": (contact_types[i] if i < len(contact_types) else "").strip(),
            }
        )

    # Social
    social_networks = request.POST.getlist("social_network[]")
    social_urls = request.POST.getlist("social_url[]")
    social_labels = request.POST.getlist("social_label[]")
    social_descs = request.POST.getlist("social_desc[]")
    socials = []
    L = max(len(social_networks), len(social_urls), len(social_labels), len(social_descs))
    for i in range(L):
        socials.append(
            {
                "network": (social_networks[i] if i < len(social_networks) else "").strip(),
                "url": (social_urls[i] if i < len(social_urls) else "").strip(),
                "label": (social_labels[i] if i < len(social_labels) else "").strip(),
                "desc": (social_descs[i] if i < len(social_descs) else "").strip(),
            }
        )

    # Galería
    images_view = request.POST.get("images_view", "list")
    images_bg = request.POST.get("images_card_bg", "0") == "1"
    images = request.POST.getlist("images[]")

    ctx = {
        "template": template,
        "full_name": full_name,
        "job_title": job_title,
        "photo": photo,
        "banner": banner,
        "video_url": video_url,
        "theme_primary": theme_primary,
        "theme_secondary": theme_secondary,
        "profile_text_primary": profile_text_primary,
        "profile_text_secondary": profile_text_secondary,
        "text_primary": text_primary,
        "text_secondary": text_secondary,
        "card_bg": card_bg,
        "block_bg": block_bg,
        "section_title": section_title,
        "section_desc": section_desc,
        "contacts": contacts,
        "socials": socials,
        "images_view": images_view,
        "images_bg": images_bg,
        "images": images,
        # flags para toggles/pills
        "globals": _get_globals(request),
    }
    return render(request, "vcards/_preview.html", ctx)


# ------------------------ API: toggles globales -------------------------
@login_required
def set_global(request):
    """
    Guarda un flag global en sesión. Espera POST con:
      - field: 'assets' | 'name' | 'title' | ...
      - enabled: 'true'/'false' o '1'/'0'
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    field = request.POST.get("field")
    enabled = request.POST.get("enabled")
    if field is None or enabled is None:
        return HttpResponseBadRequest("Missing field/enabled")

    val = str(enabled).lower() in ("1", "true", "on", "yes")
    g = request.session.get("vc_global", {})
    g[field] = val
    request.session["vc_global"] = g
    request.session.modified = True

    return JsonResponse({"ok": True, "field": field, "enabled": val})


# --------------------- API: validación de slug (HTMX) -------------------
@require_GET
@login_required
def check_slug(request):
    """
    Normaliza el valor enviado como 'slug' y responde con un fragmento HTML
    indicando si está disponible (y si cumple el mínimo de 5 caracteres).
    """
    raw = (request.GET.get("slug") or "").strip().lower()

    # Normalización idéntica al front: minúsculas, espacios→-, solo a-z0-9-
    slug = re.sub(r"\s+", "-", raw)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")

    min_ok = len(slug) >= 5

    # Si tienes modelo, consulta existencia; si no existe, asumimos disponible
    exists = False
    if min_ok and VCard is not None:
        try:
            exists = VCard.objects.filter(slug=slug).exists()
        except Exception:
            exists = False

    html = render_to_string(
        "vcards/_slug_status.html",
        {
            "available": (min_ok and not exists),
        },
    )
    return HttpResponse(html)
