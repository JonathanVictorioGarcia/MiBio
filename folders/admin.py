from django.contrib import admin
from .models import Folder

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "color", "created_at")
    search_fields = ("name", "owner__email", "owner__username")
