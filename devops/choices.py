from django.db import models


class DeploymentType(models.TextChoices):
    MANUAL = 'MANUAL', 'Manual'
    AUTOMATED = 'AUTOMATED', 'Automated'
