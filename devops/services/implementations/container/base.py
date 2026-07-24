import json
import logging
import shlex
import subprocess
from typing import Any, Dict, List, Optional

from ....exceptions import ContainerException
from ...interfaces.container import ContainerInterface


class BaseContainerService(ContainerInterface):
    """Base container engine service implementation."""

    engine: str

    def __init__(self, engine: str = 'docker') -> None:
        self.engine = engine
        self.logger = logging.getLogger(self.__class__.__name__)

    def _run(self, args: List[str], cwd: Optional[str] = None) -> str:
        command = [self.engine] + args
        self.logger.debug('Running container command: %s', ' '.join(shlex.quote(item) for item in command))
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError as exc:
            raise ContainerException(f'{self.engine} executable not found') from exc
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self.logger.error('Container command failed: %s', message)
            raise ContainerException(message or 'container command failed') from exc
        return completed.stdout.strip()

    def list_containers(self, all_containers: bool = False) -> List[Dict[str, Any]]:
        args = ['ps', '--format', '{{json .}}']
        if all_containers:
            args.insert(1, '-a')
        output = self._run(args)
        containers: List[Dict[str, Any]] = []
        for line in output.splitlines():
            if line.strip():
                containers.append(json.loads(line))
        self.logger.info('Listed %d containers', len(containers))
        return containers

    def get_container(self, container_id: str) -> Dict[str, Any]:
        output = self._run(['inspect', container_id])
        data = json.loads(output)
        self.logger.info('Retrieved container %s', container_id)
        return data[0] if isinstance(data, list) and data else data

    def create_container(self, image: str, name: Optional[str] = None, command: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> str:
        args = ['create']
        if name:
            args.extend(['--name', name])
        if env:
            for key, value in env.items():
                args.extend(['-e', f'{key}={value}'])
        args.append(image)
        if command:
            args.extend(shlex.split(command))
        container_id = self._run(args).strip()
        self.logger.info('Created container %s from image %s', container_id, image)
        return container_id

    def start_container(self, container_id: str) -> None:
        self._run(['start', container_id])
        self.logger.info('Started container %s', container_id)

    def stop_container(self, container_id: str) -> None:
        self._run(['stop', container_id])
        self.logger.info('Stopped container %s', container_id)

    def remove_container(self, container_id: str, force: bool = False) -> None:
        args = ['rm']
        if force:
            args.append('-f')
        args.append(container_id)
        self._run(args)
        self.logger.info('Removed container %s', container_id)

    def list_images(self) -> List[Dict[str, Any]]:
        output = self._run(['images', '--format', '{{json .}}'])
        images: List[Dict[str, Any]] = []
        for line in output.splitlines():
            if line.strip():
                images.append(json.loads(line))
        self.logger.info('Listed %d images', len(images))
        return images

    def pull_image(self, image: str) -> str:
        output = self._run(['pull', image])
        self.logger.info('Pulled image %s', image)
        return output
