from django.conf import settings
from django.db import models
import uuid


class Environment(models.Model):
    """Represents a deployment environment such as dev, test, or production."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Environment'
        verbose_name_plural = 'Environments'

    def __str__(self):
        return self.name


class SSHCredential(models.Model):
    """SSH credentials used to access remote infrastructure."""

    name = models.CharField(max_length=150)
    username = models.CharField(max_length=150)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=22)
    private_key = models.TextField(blank=True)
    public_key = models.TextField(blank=True)
    passphrase = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ssh_credentials',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'SSH Credential'
        verbose_name_plural = 'SSH Credentials'
        unique_together = ('name', 'host', 'port')

    def __str__(self):
        return f"{self.name} @{self.host}:{self.port}"


class GitRepository(models.Model):
    """Repository metadata for Git-managed application sources."""

    class Provider(models.TextChoices):
        GITHUB = 'GITHUB', 'GitHub'
        GITLAB = 'GITLAB', 'GitLab'
        BITBUCKET = 'BITBUCKET', 'Bitbucket'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=150)
    url = models.URLField()
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.OTHER)
    default_branch = models.CharField(max_length=100, default='main')
    project = models.ForeignKey(
        'projects.ProjetApplicatif',
        on_delete=models.CASCADE,
        related_name='git_repositories',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Git Repository'
        verbose_name_plural = 'Git Repositories'
        unique_together = ('url', 'provider')

    def __str__(self):
        return self.name


class Hypervisor(models.Model):
    """Represents a virtualization host or hypervisor platform."""

    class Provider(models.TextChoices):
        VMWARE = 'VMWARE', 'VMware'
        HYPERV = 'HYPERV', 'Hyper-V'
        KVM = 'KVM', 'KVM'
        XEN = 'XEN', 'Xen'
        PROXMOX = 'PROXMOX', 'Proxmox'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=150)
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.OTHER)
    endpoint = models.URLField(blank=True)
    management_port = models.PositiveIntegerField(default=443)
    credential = models.ForeignKey(
        SSHCredential,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hypervisors',
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hypervisor'
        verbose_name_plural = 'Hypervisors'

    def __str__(self):
        return self.name


class VirtualMachine(models.Model):
    """Represents a managed virtual machine on a hypervisor."""

    class Status(models.TextChoices):
        STOPPED = 'STOPPED', 'Stopped'
        RUNNING = 'RUNNING', 'Running'
        PAUSED = 'PAUSED', 'Paused'
        ERROR = 'ERROR', 'Error'

    name = models.CharField(max_length=150)
    uuid = models.CharField(max_length=100, unique=True)
    hypervisor = models.ForeignKey(
        Hypervisor,
        on_delete=models.CASCADE,
        related_name='virtual_machines',
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    operating_system = models.CharField(max_length=150, blank=True)
    cpu = models.PositiveIntegerField(default=1)
    memory_mb = models.PositiveIntegerField(default=1024)
    disk_gb = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.STOPPED)
    ssh_credential = models.ForeignKey(
        SSHCredential,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='virtual_machines',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Virtual Machine'
        verbose_name_plural = 'Virtual Machines'
        unique_together = ('name', 'hypervisor')

    def __str__(self):
        return self.name


class DeploymentTarget(models.Model):
    """Represents a deployment destination such as a VM or container."""

    class TargetType(models.TextChoices):
        VIRTUAL_MACHINE = 'VIRTUAL_MACHINE', 'Virtual Machine'
        DOCKER_CONTAINER = 'DOCKER_CONTAINER', 'Docker Container'
        KUBERNETES = 'KUBERNETES', 'Kubernetes'
        SERVER = 'SERVER', 'Server'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=150)
    environment = models.ForeignKey(
        Environment,
        on_delete=models.PROTECT,
        related_name='deployment_targets',
    )
    target_type = models.CharField(max_length=30, choices=TargetType.choices, default=TargetType.SERVER)
    hypervisor = models.ForeignKey(
        Hypervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deployment_targets',
    )
    virtual_machine = models.ForeignKey(
        VirtualMachine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deployment_targets',
    )
    description = models.TextField(blank=True)
    host = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(default=22)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Deployment Target'
        verbose_name_plural = 'Deployment Targets'
        unique_together = ('name', 'environment')

    def __str__(self):
        return self.name


class DockerImage(models.Model):
    """Represents a Docker image available for deployment."""

    name = models.CharField(max_length=150)
    tag = models.CharField(max_length=100, default='latest')
    repository_url = models.URLField(blank=True)
    digest = models.CharField(max_length=255, blank=True)
    environment = models.ForeignKey(
        Environment,
        on_delete=models.PROTECT,
        related_name='docker_images',
        null=True,
        blank=True,
    )
    labels = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Docker Image'
        verbose_name_plural = 'Docker Images'
        unique_together = ('name', 'tag')

    def __str__(self):
        return f"{self.name}:{self.tag}"


class DockerContainer(models.Model):
    """Represents a running or stopped Docker container."""

    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        RUNNING = 'RUNNING', 'Running'
        PAUSED = 'PAUSED', 'Paused'
        STOPPED = 'STOPPED', 'Stopped'
        REMOVED = 'REMOVED', 'Removed'

    name = models.CharField(max_length=150)
    image = models.ForeignKey(
        DockerImage,
        on_delete=models.CASCADE,
        related_name='containers',
    )
    virtual_machine = models.ForeignKey(
        VirtualMachine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='docker_containers',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Docker Container'
        verbose_name_plural = 'Docker Containers'
        unique_together = ('name', 'virtual_machine')

    def __str__(self):
        return self.name


class TerraformWorkspace(models.Model):
    """Represents a Terraform workspace used for infrastructure deployment."""

    name = models.CharField(max_length=150)
    project = models.ForeignKey(
        'projects.ProjetApplicatif',
        on_delete=models.CASCADE,
        related_name='terraform_workspaces',
        null=True,
        blank=True,
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.PROTECT,
        related_name='terraform_workspaces',
        null=True,
        blank=True,
    )
    path = models.CharField(max_length=255, blank=True)
    variables = models.JSONField(default=dict, blank=True)
    backend_config = models.JSONField(default=dict, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Terraform Workspace'
        verbose_name_plural = 'Terraform Workspaces'
        unique_together = ('name', 'project')

    def __str__(self):
        return self.name


class AnsiblePlaybook(models.Model):
    """Represents an Ansible playbook definition."""

    name = models.CharField(max_length=150)
    repository_url = models.URLField(blank=True)
    path = models.CharField(max_length=255, blank=True)
    environment = models.ForeignKey(
        Environment,
        on_delete=models.PROTECT,
        related_name='ansible_playbooks',
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ansible Playbook'
        verbose_name_plural = 'Ansible Playbooks'
        unique_together = ('name', 'repository_url')

    def __str__(self):
        return self.name


class Pipeline(models.Model):
    """Represents a deployment pipeline that composes tasks and environments."""

    name = models.CharField(max_length=150)
    project = models.ForeignKey(
        'projects.ProjetApplicatif',
        on_delete=models.CASCADE,
        related_name='pipelines',
        null=True,
        blank=True,
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.PROTECT,
        related_name='pipelines',
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pipelines',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pipeline'
        verbose_name_plural = 'Pipelines'

    def __str__(self):
        return self.name


class DeploymentTask(models.Model):
    """Represents a workflow task executed by the DevOps engine."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    name = models.CharField(max_length=150)
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
    )
    deployment_target = models.ForeignKey(
        DeploymentTarget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deployment_tasks',
    )
    project = models.ForeignKey(
        'projects.ProjetApplicatif',
        on_delete=models.CASCADE,
        related_name='deployment_tasks',
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deployment_tasks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Deployment Task'
        verbose_name_plural = 'Deployment Tasks'

    def __str__(self):
        return self.name


class DeploymentLog(models.Model):
    """Execution log entries for deployment tasks."""

    class Level(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        ERROR = 'ERROR', 'Error'

    task = models.ForeignKey(
        DeploymentTask,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.INFO)
    message = models.TextField()
    source = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = 'Deployment Log'
        verbose_name_plural = 'Deployment Logs'

    def __str__(self):
        return f"[{self.level}] {self.message[:80]}"


class EnvironmentVariable(models.Model):
    """Represents a named environment variable scoped to a project or environment."""

    key = models.CharField(max_length=150)
    value = models.TextField(blank=True)
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name='variables',
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        'projects.ProjetApplicatif',
        on_delete=models.CASCADE,
        related_name='variables',
        null=True,
        blank=True,
    )
    is_secret = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Environment Variable'
        verbose_name_plural = 'Environment Variables'
        unique_together = ('key', 'environment', 'project')

    def __str__(self):
        return self.key


class Secret(models.Model):
    """Stores sensitive values for the DevOps domain."""

    name = models.CharField(max_length=150)
    key = models.CharField(max_length=150)
    value = models.TextField()
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name='secrets',
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        'projects.ProjetApplicatif',
        on_delete=models.CASCADE,
        related_name='secrets',
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secrets',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Secret'
        verbose_name_plural = 'Secrets'
        unique_together = ('key', 'environment', 'project')

    def __str__(self):
        return self.name


class Artifact(models.Model):
    """Represents an artifact generated during a deployment or pipeline run."""

    name = models.CharField(max_length=150)
    artifact_type = models.CharField(max_length=100, blank=True)
    project = models.ForeignKey(
        'projects.ProjetApplicatif',
        on_delete=models.CASCADE,
        related_name='artifacts',
        null=True,
        blank=True,
    )
    deployment_task = models.ForeignKey(
        DeploymentTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='artifacts',
    )
    path = models.CharField(max_length=255, blank=True)
    checksum = models.CharField(max_length=255, blank=True)
    size_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Artifact'
        verbose_name_plural = 'Artifacts'

    def __str__(self):
        return self.name


class GenerationHistory(models.Model):
    """Tracks generated DevOps artifact execution history for audit and monitoring."""

    project_name = models.CharField(max_length=150)
    framework = models.CharField(max_length=50, blank=True)
    provider = models.CharField(max_length=50, blank=True)
    ci_platform = models.CharField(max_length=50, blank=True)
    artifacts_generated = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default='SUCCESS')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Generation History'
        verbose_name_plural = 'Generation Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"GenerationHistory({self.project_name} - {self.framework} @ {self.created_at})"


# ======================================================================
# Phase 11 — Asynchronous Deployment & Persistent Monitoring
# ======================================================================


class DeploymentJob(models.Model):
    """An asynchronous deployment job — the queue unit."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        QUEUED = 'QUEUED', 'Queued'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        ROLLING_BACK = 'ROLLING_BACK', 'Rolling Back'
        ROLLED_BACK = 'ROLLED_BACK', 'Rolled Back'

    deployment_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    provider_name = models.CharField(max_length=50)
    project_data = models.JSONField()
    artifacts_data = models.JSONField()
    config_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    current_stage = models.CharField(max_length=50, blank=True)
    progress_percent = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deployment Job'
        verbose_name_plural = 'Deployment Jobs'

    def __str__(self):
        return f"DeploymentJob({self.deployment_id} - {self.status})"


class DeploymentStageProgress(models.Model):
    """Tracks individual stage progress within a deployment job."""

    class StageStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        SKIPPED = 'SKIPPED', 'Skipped'

    job = models.ForeignKey(
        DeploymentJob,
        on_delete=models.CASCADE,
        related_name='stages',
    )
    stage_name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=StageStatus.choices, default=StageStatus.PENDING)
    progress_percent = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Deployment Stage Progress'
        verbose_name_plural = 'Deployment Stage Progress'

    def __str__(self):
        return f"{self.stage_name} ({self.status})"


class DeploymentLogEntry(models.Model):
    """Persistent log entry for a deployment job."""

    class Level(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        ERROR = 'ERROR', 'Error'

    job = models.ForeignKey(
        DeploymentJob,
        on_delete=models.CASCADE,
        related_name='log_entries',
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    message = models.TextField()
    stage = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Deployment Log Entry'
        verbose_name_plural = 'Deployment Log Entries'

    def __str__(self):
        return f"[{self.level}] {self.message[:80]}"


class DeploymentEvent(models.Model):
    """Event published during deployment for monitoring and future WebSocket integration."""

    job = models.ForeignKey(
        DeploymentJob,
        on_delete=models.CASCADE,
        related_name='events',
    )
    event_type = models.CharField(max_length=50)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Deployment Event'
        verbose_name_plural = 'Deployment Events'

    def __str__(self):
        return f"{self.event_type} ({self.created_at})"

