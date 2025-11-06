from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        USER = "USER", "Usuario"
        
        

    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.USER,
        help_text="Rol del usuario para redirecciones y permisos."
    )

    def is_admin(self) -> bool:
        return self.role == self.Roles.ADMIN

    def is_user(self) -> bool:
        return self.role == self.Roles.USER
