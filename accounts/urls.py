from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, MeView, LoginView,
    GithubAuthURLView, GithubCallbackView,
    GoogleAuthURLView, GoogleCallbackView,
    UtilisateurListView, UtilisateurDetailView, ChangerRoleView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login-refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('github/url/', GithubAuthURLView.as_view(), name='github-url'),
    path('github/callback/', GithubCallbackView.as_view(), name='github-callback'),
    path('google/url/', GoogleAuthURLView.as_view(), name='google-url'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    path('users/', UtilisateurListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UtilisateurDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/role/', ChangerRoleView.as_view(), name='user-role'),
]