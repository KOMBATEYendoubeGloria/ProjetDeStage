from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        DEVOPS = 'DEVOPS', 'DevOps'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.DEVOPS,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"