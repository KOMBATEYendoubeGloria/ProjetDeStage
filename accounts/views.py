from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .permissions import IsAdmin, IsAdminOrSelf
from django.contrib.auth import login
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from social_django.utils import psa
import requests as http_requests
from decouple import config

from .models import Utilisateur
from .serializers import RegisterSerializer, UtilisateurSerializer


class RegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


LoginView = TokenObtainPairView


class GithubAuthURLView(APIView):
    """Renvoie l'URL de connexion GitHub au frontend"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        client_id = config('GITHUB_CLIENT_ID')
        redirect_uri = 'http://localhost:8000/api/auth/github/callback/'
        url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=user:email"
        )
        return Response({'url': url})


class GithubCallbackView(APIView):
    """Reçoit le code GitHub, crée/récupère l'utilisateur et renvoie un JWT"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'Code manquant'}, status=400)

        # echanger le code contre un access token GitHub
        token_response = http_requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': config('GITHUB_CLIENT_ID'),
                'client_secret': config('GITHUB_CLIENT_SECRET'),
                'code': code,
            },
            headers={'Accept': 'application/json'}
        )
        token_data = token_response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            return Response({'error': 'Token GitHub invalide'}, status=400)

        # Recupérer les infos de l'utilisateur GitHub
        user_response = http_requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'token {access_token}'}
        )
        github_user = user_response.json()

        # Recupérer l'email si pas public
        email = github_user.get('email')
        if not email:
            emails_response = http_requests.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f'token {access_token}'}
            )
            emails = emails_response.json()
            email = next(
                (e['email'] for e in emails if e['primary']),
                f"{github_user['login']}@github.com"
            )

        # Créer ou récupérer l'utilisateur
        user, created = Utilisateur.objects.get_or_create(
            username=github_user['login'],
            defaults={
                'email': email,
                'role': Utilisateur.Role.DEVOPS,
            }
        )

        # Générer le JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created': created,
            }
        })
    

class GoogleAuthURLView(APIView):
    """Renvoie l'URL de connexion Google au frontend"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        client_id = config('GOOGLE_CLIENT_ID')
        redirect_uri = 'http://localhost:8000/api/auth/google/callback/'
        url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=openid%20email%20profile"
        )
        return Response({'url': url})


class GoogleCallbackView(APIView):
    """Reçoit le code Google, crée/récupère l'utilisateur et renvoie un JWT"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'Code manquant'}, status=400)

        # echange le code contre un access token Google
        token_response = http_requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': config('GOOGLE_CLIENT_ID'),
                'client_secret': config('GOOGLE_CLIENT_SECRET'),
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://localhost:8000/api/auth/google/callback/',
            }
        )
        token_data = token_response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            return Response({'error': 'Token Google invalide', 'details': token_data}, status=400)

        # por rcupérer les infos de l'utilisateur Google
        user_response = http_requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        google_user = user_response.json()

        email = google_user.get('email')
        if not email:
            return Response({'error': 'Email Google non disponible'}, status=400)

        # Créer un username à partir de l'email
        username = email.split('@')[0]

        # Créer ou récupérer l'utilisateur
        user, created = Utilisateur.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'role': Utilisateur.Role.DEVOPS,
            }
        )

        # Générer le JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created': created,
            }
        })    




class UtilisateurListView(generics.ListAPIView):
    """Liste tous les utilisateurs — réservé aux Admins"""
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = Utilisateur.objects.all()
        # Filtrage optionnel par rôle : /api/auth/users/?role=ADMIN
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class UtilisateurDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'un utilisateur"""
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
    queryset = Utilisateur.objects.all()

    def update(self, request, *args, **kwargs):
        # Seul un Admin peut changer le rôle
        if 'role' in request.data and request.user.role != 'ADMIN':
            return Response(
                {'error': 'Seul un Admin peut modifier le rôle'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class ChangerRoleView(generics.UpdateAPIView):
    """Changer le rôle d'un utilisateur — réservé aux Admins"""
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAdmin]
    queryset = Utilisateur.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        role = request.data.get('role')
        if role not in ['ADMIN', 'DEVOPS']:
            return Response(
                {'error': 'Rôle invalide. Choisir ADMIN ou DEVOPS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.role = role
        user.save()
        return Response({
            'message': f"Rôle de {user.username} changé en {role}",
            'user': UtilisateurSerializer(user).data
        })    