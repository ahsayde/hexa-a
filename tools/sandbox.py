import docker
import os
from tools.tools import read_config

class Sandbox:
    def __init__(self):
        self._docker = docker.from_env()
        self._config = read_config()['sandbox']
        self.image = self._config['image']
        self.user = self._config['user']
        self.working_dir = self._config['workdir']
        self.mem_limit = self._config['mem_limit']
        self.mounts = self._config['mounts']

    def create(self, user_path):
        mounts = [{
            'Source': os.path.join(self.mounts, user_path),
            'Target': self.working_dir,
            'Type': 'bind',
            'ReadOnly': False
        }]
        container = self._docker.containers.create(
            image=self.image,
            user=self.user,
            working_dir=self.working_dir, 
            mounts=mounts,
            mem_limit=self.mem_limit,
            network_disabled=True,
            tty=True
        )
        return container

    def start(self, cid):
        self._docker.api.start(cid)

    def remove(self, cid):
        self._docker.api.remove_container(cid, force=True)

    def execute(self, cid, cmd):
        result = {}
        response = self._docker.api.exec_create(cid, cmd, tty=True)
        exec_id = response['Id']

        try:
            output = self._docker.api.exec_start(exec_id)
        except MemoryError:
            result['output'] = 'Memory Error'
            result['status'] = 'ERROR'
        except IOError:
            result['output'] = 'I/O Error'
            result['status'] = 'ERROR'
        finally:
            inspect =  self._docker.api.exec_inspect(exec_id)
            if inspect['ExitCode']:
                result['output'] = output.decode('utf-8')
                result['status'] = 'ERROR'
            else:
                result['output'] = output.decode('utf-8')             
                result['status'] = 'SUCCESS'

            result['returncode'] = inspect['ExitCode']
            
        return result