from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import Utilisateur


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Cherche l'utilisateur par username o u par email
            user = Utilisateur.objects.get(
                Q(username=username) | Q(email=username)
            )
        except Utilisateur.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None