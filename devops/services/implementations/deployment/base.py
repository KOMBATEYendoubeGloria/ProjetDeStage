import logging
from typing import Any, Dict, List, Optional

from ....exceptions import DeploymentException
from ...interfaces.deployment import DeploymentInterface


class BaseDeploymentService(DeploymentInterface):
    """Base deployment service implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.deployments: Dict[str, Dict[str, Any]] = {}

    def prepare(self, deployment_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.deployments[deployment_id] = {
            'id': deployment_id,
            'metadata': metadata or {},
            'status': 'prepared',
        }
        self.logger.info('Prepared deployment %s', deployment_id)

    def execute(self, deployment_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            raise DeploymentException('Deployment not found')
        deployment['status'] = 'running'
        deployment['parameters'] = parameters or {}
        self.logger.info('Executed deployment %s', deployment_id)
        return {
            'deployment_id': deployment_id,
            'status': deployment['status'],
            'parameters': deployment['parameters'],
        }

    def cancel(self, deployment_id: str) -> None:
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            raise DeploymentException('Deployment not found')
        deployment['status'] = 'cancelled'
        self.logger.info('Cancelled deployment %s', deployment_id)

    def status(self, deployment_id: str) -> Dict[str, Any]:
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            raise DeploymentException('Deployment not found')
        self.logger.info('Retrieved status for deployment %s', deployment_id)
        return deployment

    def list_deployments(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self.logger.info('Listed deployments')
        return [deployment for deployment in self.deployments.values() if not project_id or deployment['metadata'].get('project_id') == project_id]
