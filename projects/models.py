from django.conf import settings
from django.db import models


class ProjetApplicatif(models.Model):
    class Technologie(models.TextChoices):
        NODEJS = 'NODEJS', 'Node.js'
        DJANGO = 'DJANGO', 'Django'
        REACT = 'REACT', 'React'
        

    nom = models.CharField(max_length=100)
    url_depot_git = models.URLField()
    technologie = models.CharField(max_length=10, choices=Technologie.choices)
    branche = models.CharField(max_length=50, default='main')
    variables_env = models.JSONField(default=dict, blank=True)

    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projets',
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom