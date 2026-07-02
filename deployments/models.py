from django.db import models
from projects.models import ProjetApplicatif


class Deploiement(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        EN_COURS = 'EN_COURS', 'En cours'
        SUCCES = 'SUCCES', 'Succès'
        ECHEC = 'ECHEC', 'Échec'

    projet = models.ForeignKey(
        ProjetApplicatif,
        on_delete=models.CASCADE,
        related_name='deploiements',
    )
    date_heure = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=15,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE,
    )
    commit_hash = models.CharField(max_length=40, blank=True)
    script_genere = models.TextField(blank=True)

    def __str__(self):
        return f"Déploiement #{self.id} - {self.projet.nom} ({self.statut})"


class Journal(models.Model):
    class Niveau(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARN = 'WARN', 'Avertissement'
        ERROR = 'ERROR', 'Erreur'

    deploiement = models.ForeignKey(
        Deploiement,
        on_delete=models.CASCADE,
        related_name='journaux',
    )
    horodatage = models.DateTimeField(auto_now_add=True)
    niveau = models.CharField(max_length=10, choices=Niveau.choices, default=Niveau.INFO)
    message = models.TextField()
    source = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"[{self.niveau}] {self.message[:50]}"