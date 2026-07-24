"""URL configuration for the DevOps API."""

from django.urls import path

from devops.api.views.analyze import AnalyzeView
from devops.api.views.artifacts import (
    AllArtifactsView,
    AnsibleView,
    DockerComposeView,
    DockerfileView,
    EnvironmentView,
    PipelineView,
    TerraformView,
)
from devops.api.views.health import HealthCheckView
from devops.api.views.history import GenerationHistoryDetailView, GenerationHistoryListView

app_name = 'devops-api'

urlpatterns = [
    # Analysis
    path('analyze/', AnalyzeView.as_view(), name='analyze'),

    # Individual artifact generation
    path('artifacts/docker/', DockerfileView.as_view(), name='dockerfile'),
    path('artifacts/docker-compose/', DockerComposeView.as_view(), name='docker-compose'),
    path('artifacts/environment/', EnvironmentView.as_view(), name='environment'),
    path('artifacts/terraform/', TerraformView.as_view(), name='terraform'),
    path('artifacts/ansible/', AnsibleView.as_view(), name='ansible'),
    path('artifacts/pipeline/', PipelineView.as_view(), name='pipeline'),
    path('artifacts/all/', AllArtifactsView.as_view(), name='all-artifacts'),

    # Generation history
    path('history/', GenerationHistoryListView.as_view(), name='history-list'),
    path('history/<int:pk>/', GenerationHistoryDetailView.as_view(), name='history-detail'),

    # Health check
    path('health/', HealthCheckView.as_view(), name='health'),
]
