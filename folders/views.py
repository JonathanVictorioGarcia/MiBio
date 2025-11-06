# folders/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.db import IntegrityError

from .models import Folder


@login_required
def folders_chips(request):
    """
    Devuelve el fragmento con los chips (lista de carpetas del usuario).
    Este view se usa como respuesta HTMX para refrescar la tira de chips.
    """
    folders = Folder.objects.filter(owner=request.user).order_by("name")
    return render(request, "folders/_chips.html", {"folders": folders})


@login_required
def folder_save(request):
    """
    ÚNICO endpoint para crear/editar.
    - Si viene id -> edita
    - Si no viene id -> crea
    Devuelve el fragmento de chips actualizado.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST requerido")

    fid   = (request.POST.get("id") or "").strip()
    name  = (request.POST.get("name") or "").strip()
    color = (request.POST.get("color") or "#6366f1").strip()

    if len(name) < 2:
        return HttpResponseBadRequest("Nombre inválido")

    try:
        if fid:
            try:
                f = Folder.objects.get(id=fid, owner=request.user)
            except Folder.DoesNotExist:
                return HttpResponseBadRequest("No existe")
            f.name = name
            f.color = color
            f.save()
        else:
            Folder.objects.create(owner=request.user, name=name, color=color)
    except IntegrityError:
        # Tu modelo tiene unique_together (owner, name)
        return HttpResponseBadRequest("Ya existe una carpeta con ese nombre")

    return folders_chips(request)


@login_required
def folder_delete(request):
    """
    Elimina una carpeta del usuario. (Las tarjetas pueden desvincularse aquí si lo deseas)
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST requerido")

    fid = request.POST.get("id")
    try:
        f = Folder.objects.get(id=fid, owner=request.user)
    except Folder.DoesNotExist:
        return HttpResponseBadRequest("No existe")

    # Opcional: dejar las tarjetas "sin carpeta"
    # from vcards.models import VCard
    # VCard.objects.filter(owner=request.user, folder=f).update(folder=None)

    f.delete()
    return folders_chips(request)

@login_required
def folders_options(request):
    """
    Devuelve SOLO las <option> del selector de carpetas del usuario.
    Se usa para refrescar el <select> vía HTMX.
    """
    folders = Folder.objects.filter(owner=request.user).order_by("name")
    return render(request, "folders/_options.html", {"folders": folders})