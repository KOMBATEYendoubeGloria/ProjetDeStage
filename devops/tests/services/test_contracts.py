from inspect import signature

from django.test import SimpleTestCase

from devops.services.interfaces.artifact import ArtifactInterface
from devops.services.interfaces.configuration import ConfigurationInterface
from devops.services.interfaces.container import ContainerInterface
from devops.services.interfaces.deployment import DeploymentInterface
from devops.services.interfaces.environment import EnvironmentInterface
from devops.services.interfaces.git import GitInterface
from devops.services.interfaces.hypervisor import HypervisorInterface
from devops.services.interfaces.infrastructure import InfrastructureInterface
from devops.services.interfaces.logging import LoggingInterface
from devops.services.interfaces.monitoring import MonitoringInterface
from devops.services.interfaces.notification import NotificationInterface
from devops.services.interfaces.pipeline import PipelineInterface
from devops.services.interfaces.repository import RepositoryInterface
from devops.services.interfaces.secret import SecretInterface
from devops.services.interfaces.ssh import SSHInterface

from devops.services.implementations.artifact.default import DefaultArtifactService
from devops.services.implementations.configuration.default import DefaultConfigurationService
from devops.services.implementations.container.docker import DockerService
from devops.services.implementations.deployment.default import DefaultDeploymentService
from devops.services.implementations.environment.default import DefaultEnvironmentService
from devops.services.implementations.git.github import GitHubService
from devops.services.implementations.hypervisors.proxmox import ProxmoxService
from devops.services.implementations.infrastructure.terraform_service import TerraformService
from devops.services.implementations.logging.default import DefaultLoggingService
from devops.services.implementations.monitoring.default import DefaultMonitoringService
from devops.services.implementations.notification.email import EmailNotificationService
from devops.services.implementations.pipeline.default import DefaultPipelineService
from devops.services.implementations.repository.default import DefaultRepositoryService
from devops.services.implementations.secret.default import DefaultSecretService
from devops.services.implementations.ssh.paramiko_ssh_service import ParamikoSSHService


class ServiceContractTests(SimpleTestCase):
    def assert_signature_match(self, interface_class, implementation_class, method_name):
        expected = signature(getattr(interface_class, method_name))
        actual = signature(getattr(implementation_class, method_name))
        self.assertEqual(str(actual), str(expected), f'Signature mismatch for {implementation_class.__name__}.{method_name}')

    def assert_instantiable(self, implementation_class, *args, **kwargs):
        if implementation_class is ParamikoSSHService:
            return implementation_class()
        instance = implementation_class(*args, **kwargs)
        self.assertFalse(getattr(implementation_class, '__abstractmethods__', False), f'{implementation_class.__name__} still has abstract methods')
        return instance

    def test_git_contract(self):
        self.assert_signature_match(GitInterface, GitHubService, 'clone')
        self.assert_signature_match(GitInterface, GitHubService, 'pull')
        self.assert_signature_match(GitInterface, GitHubService, 'fetch')
        self.assert_signature_match(GitInterface, GitHubService, 'checkout')
        self.assert_signature_match(GitInterface, GitHubService, 'commit')
        self.assert_signature_match(GitInterface, GitHubService, 'push')
        self.assert_signature_match(GitInterface, GitHubService, 'list_branches')
        self.assert_signature_match(GitInterface, GitHubService, 'get_current_branch')
        self.assert_signature_match(GitInterface, GitHubService, 'get_status')
        self.assert_instantiable(GitHubService)

    def test_container_contract(self):
        self.assert_signature_match(ContainerInterface, DockerService, 'list_containers')
        self.assert_signature_match(ContainerInterface, DockerService, 'get_container')
        self.assert_signature_match(ContainerInterface, DockerService, 'create_container')
        self.assert_signature_match(ContainerInterface, DockerService, 'start_container')
        self.assert_signature_match(ContainerInterface, DockerService, 'stop_container')
        self.assert_signature_match(ContainerInterface, DockerService, 'remove_container')
        self.assert_signature_match(ContainerInterface, DockerService, 'list_images')
        self.assert_signature_match(ContainerInterface, DockerService, 'pull_image')
        self.assert_instantiable(DockerService)

    def test_infrastructure_contract(self):
        self.assert_signature_match(InfrastructureInterface, TerraformService, 'init')
        self.assert_signature_match(InfrastructureInterface, TerraformService, 'validate')
        self.assert_signature_match(InfrastructureInterface, TerraformService, 'plan')
        self.assert_signature_match(InfrastructureInterface, TerraformService, 'apply')
        self.assert_signature_match(InfrastructureInterface, TerraformService, 'destroy')
        self.assert_signature_match(InfrastructureInterface, TerraformService, 'output')
        self.assert_signature_match(InfrastructureInterface, TerraformService, 'workspace')
        self.assert_instantiable(TerraformService)

    def test_ssh_contract(self):
        self.assert_signature_match(SSHInterface, ParamikoSSHService, 'connect')
        self.assert_signature_match(SSHInterface, ParamikoSSHService, 'execute')
        self.assert_signature_match(SSHInterface, ParamikoSSHService, 'copy')
        self.assert_signature_match(SSHInterface, ParamikoSSHService, 'close')

    def test_hypervisor_contract(self):
        self.assert_signature_match(HypervisorInterface, ProxmoxService, 'create_vm')
        self.assert_signature_match(HypervisorInterface, ProxmoxService, 'delete_vm')
        self.assert_signature_match(HypervisorInterface, ProxmoxService, 'start_vm')
        self.assert_signature_match(HypervisorInterface, ProxmoxService, 'stop_vm')
        self.assert_signature_match(HypervisorInterface, ProxmoxService, 'reboot_vm')
        self.assert_signature_match(HypervisorInterface, ProxmoxService, 'snapshot_vm')
        self.assert_signature_match(HypervisorInterface, ProxmoxService, 'restore_snapshot')
        self.assert_signature_match(HypervisorInterface, ProxmoxService, 'list_vms')
        self.assert_instantiable(ProxmoxService)

    def test_deployment_contract(self):
        self.assert_signature_match(DeploymentInterface, DefaultDeploymentService, 'prepare')
        self.assert_signature_match(DeploymentInterface, DefaultDeploymentService, 'execute')
        self.assert_signature_match(DeploymentInterface, DefaultDeploymentService, 'cancel')
        self.assert_signature_match(DeploymentInterface, DefaultDeploymentService, 'status')
        self.assert_signature_match(DeploymentInterface, DefaultDeploymentService, 'list_deployments')
        self.assert_instantiable(DefaultDeploymentService)

    def test_pipeline_contract(self):
        self.assert_signature_match(PipelineInterface, DefaultPipelineService, 'create_pipeline')
        self.assert_signature_match(PipelineInterface, DefaultPipelineService, 'execute_pipeline')
        self.assert_signature_match(PipelineInterface, DefaultPipelineService, 'suspend_pipeline')
        self.assert_signature_match(PipelineInterface, DefaultPipelineService, 'resume_pipeline')
        self.assert_signature_match(PipelineInterface, DefaultPipelineService, 'get_pipeline_status')
        self.assert_signature_match(PipelineInterface, DefaultPipelineService, 'list_pipeline_runs')
        self.assert_instantiable(DefaultPipelineService)

    def test_monitoring_contract(self):
        self.assert_signature_match(MonitoringInterface, DefaultMonitoringService, 'get_metrics')
        self.assert_signature_match(MonitoringInterface, DefaultMonitoringService, 'get_status')
        self.assert_signature_match(MonitoringInterface, DefaultMonitoringService, 'get_alerts')
        self.assert_signature_match(MonitoringInterface, DefaultMonitoringService, 'get_events')
        self.assert_instantiable(DefaultMonitoringService)

    def test_logging_contract(self):
        self.assert_signature_match(LoggingInterface, DefaultLoggingService, 'log_event')
        self.assert_signature_match(LoggingInterface, DefaultLoggingService, 'query_logs')
        self.assert_signature_match(LoggingInterface, DefaultLoggingService, 'get_log_summary')
        self.assert_instantiable(DefaultLoggingService)

    def test_notification_contract(self):
        self.assert_signature_match(NotificationInterface, EmailNotificationService, 'send_notification')
        self.assert_signature_match(NotificationInterface, EmailNotificationService, 'list_channels')
        self.assert_instantiable(EmailNotificationService)

    def test_configuration_contract(self):
        self.assert_signature_match(ConfigurationInterface, DefaultConfigurationService, 'get_configuration')
        self.assert_signature_match(ConfigurationInterface, DefaultConfigurationService, 'set_configuration')
        self.assert_signature_match(ConfigurationInterface, DefaultConfigurationService, 'validate_configuration')
        self.assert_instantiable(DefaultConfigurationService)

    def test_repository_contract(self):
        self.assert_signature_match(RepositoryInterface, DefaultRepositoryService, 'list_repositories')
        self.assert_signature_match(RepositoryInterface, DefaultRepositoryService, 'get_repository')
        self.assert_signature_match(RepositoryInterface, DefaultRepositoryService, 'add_repository')
        self.assert_signature_match(RepositoryInterface, DefaultRepositoryService, 'remove_repository')
        self.assert_instantiable(DefaultRepositoryService)

    def test_artifact_contract(self):
        self.assert_signature_match(ArtifactInterface, DefaultArtifactService, 'store_artifact')
        self.assert_signature_match(ArtifactInterface, DefaultArtifactService, 'retrieve_artifact')
        self.assert_signature_match(ArtifactInterface, DefaultArtifactService, 'list_artifacts')
        self.assert_signature_match(ArtifactInterface, DefaultArtifactService, 'delete_artifact')
        self.assert_instantiable(DefaultArtifactService)

    def test_environment_contract(self):
        self.assert_signature_match(EnvironmentInterface, DefaultEnvironmentService, 'list_environments')
        self.assert_signature_match(EnvironmentInterface, DefaultEnvironmentService, 'get_environment')
        self.assert_signature_match(EnvironmentInterface, DefaultEnvironmentService, 'create_environment')
        self.assert_signature_match(EnvironmentInterface, DefaultEnvironmentService, 'update_environment')
        self.assert_signature_match(EnvironmentInterface, DefaultEnvironmentService, 'delete_environment')
        self.assert_instantiable(DefaultEnvironmentService)

    def test_secret_contract(self):
        self.assert_signature_match(SecretInterface, DefaultSecretService, 'store_secret')
        self.assert_signature_match(SecretInterface, DefaultSecretService, 'retrieve_secret')
        self.assert_signature_match(SecretInterface, DefaultSecretService, 'list_secrets')
        self.assert_signature_match(SecretInterface, DefaultSecretService, 'delete_secret')
        self.assert_instantiable(DefaultSecretService)
