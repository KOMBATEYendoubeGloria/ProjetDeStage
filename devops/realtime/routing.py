"""WebSocket URL routing."""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/deployments/(?P<deployment_id>[0-9a-f-]+)/$', consumers.DeploymentConsumer.as_asgi()),
    re_path(r'ws/projects/(?P<project_id>[0-9a-f-]+)/$', consumers.ProjectConsumer.as_asgi()),
    re_path(r'ws/user/$', consumers.UserConsumer.as_asgi()),
]
