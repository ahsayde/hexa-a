import docker
import os

class Sandbox:
    def __init__(self):
        self._docker = docker.from_env()

    def create(self, image, path, env=None):
        mounts = [{
            'Source': os.path.join(path),
            'Target': "/data",
            'Type': 'bind',
            'ReadOnly': False
        }]
        container = self._docker.containers.create(
            image=image, 
            mounts=mounts,
            environment=env,
            network_disabled=True,
            tty=True
        )
        return container

    def start(self, cid):
        self._docker.api.start(cid)

    def remove(self, cid):
        self._docker.api.remove_container(cid, force=True)

    def wait(self, timeout=60):
        self._docker.wait(timeout=timeout)