from rest_framework import serializers
from .models import ProjetApplicatif


class ProjetApplicatifSerializer(serializers.ModelSerializer):
    proprietaire = serializers.ReadOnlyField(source='proprietaire.username')

    class Meta:
        model = ProjetApplicatif
        fields = [
            'id', 'nom', 'url_depot_git', 'technologie',
            'branche', 'variables_env', 'proprietaire', 'date_creation',
        ]
        read_only_fields = ['id', 'proprietaire', 'date_creation']