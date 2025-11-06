from django.db import models
from django.conf import settings

class Folder(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="folders")
    name  = models.CharField(max_length=60)
    color = models.CharField(max_length=9, default="#6366f1")  # admite #RRGGBB
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "name")
        ordering = ("name",)

    def __str__(self):
        return self.name
