import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Utilisateur

user = Utilisateur.objects.get(username='admin')
user.role = 'ADMIN'
user.save()
print(f"username: {user.username} | role: {user.role}")