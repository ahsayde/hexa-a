import docker
from tools.tools import read_config

class Sandbox:
    def __init__(self):
        self._docker = docker.from_env()
        self._config = read_config()['sandbox']

    def create(self, user_path, environment):
        self._config['mounts'][0]['Source'] += '/' + user_path 
        container = self._docker.containers.create(
            image=self._config['image'],
            user=self._config['user'],
            working_dir=self._config['workdir'],
            mounts=self._config['mounts'],
            network_disabled=True,
            tty=True,
            environment=environment
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
            result['stdout'] = ''
            result['stderr'] = 'Memory error'
            result['status'] = 'ERROR'
            
            
        inspect =  self._docker.api.exec_inspect(exec_id)
        
        if inspect['ExitCode']:
            result['stdout'] = ''
            result['stderr'] = output
            result['status'] = 'ERROR'
        else:
            result['status'] = 'SUCCESS'
            result['stdout'] = output
            result['stderr'] = ''

        result['returncode'] = inspect['ExitCode']

        return result