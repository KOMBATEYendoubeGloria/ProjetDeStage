from rest_framework import serializers
from .models import Deploiement, Journal


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'horodatage', 'niveau', 'message', 'source']
        read_only_fields = ['id', 'horodatage']


class DeploiementSerializer(serializers.ModelSerializer):
    projet_nom = serializers.ReadOnlyField(source='projet.nom')
    journaux = JournalSerializer(many=True, read_only=True)

    class Meta:
        model = Deploiement
        fields = [
            'id', 'projet', 'projet_nom', 'date_heure',
            'statut', 'commit_hash', 'script_genere', 'journaux',
        ]
        read_only_fields = ['id', 'date_heure', 'statut', 'script_genere']