from enum import Enum


class DevopsComponent(Enum):
    SERVICES = 'services'
    DEPLOYMENT = 'deployment'
    TERRAFORM = 'terraform'
    DOCKER = 'docker'
    ANSIBLE = 'ansible'
    GIT = 'git'
    SSH = 'ssh'
    HYPERVISORS = 'hypervisors'
    PIPELINES = 'pipelines'
    MONITORING = 'monitoring'
    LOGGING = 'logging'
