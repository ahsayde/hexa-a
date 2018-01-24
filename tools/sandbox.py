from tools.tools import execute

class Sandbox:
    def __init__(self):
        pass
                       
    def list(self):
        cmd = 'docker ps -a -q'
        response = execute(cmd)
        return response.stdout.split()
        
    def create(self, image, workdir='/usr/src'):
        cmd = 'docker create -w {workdir} -it {image}'.format(workdir=workdir, image=image)
        response = execute(cmd)
        identifier = response.stdout.strip()
        return Container(identifier=identifier)

class Container:
    def __init__(self, identifier):
        self.__identifier = identifier

    def start(self):
        cmd = 'docker start {identifier}'.format(identifier=self.__identifier)
        execute(cmd)

    def stop(self):
        cmd = 'docker stop {identifier}'.format(identifier=self.__identifier)
        execute(cmd)

    def remove(self, force=True):
        if force:
            cmd = 'docker rm -f {identifier}'
        else:
            cmd = 'docker rm {identifier}'

        execute(cmd.format(identifier=self.__identifier))
    
    def upload(self, source, destination='/usr/src'):
        cmd = 'docker cp {source} {identifier}:{destination}'.format(
            source=source,
            destination=destination,
            identifier=self.__identifier,
        )
        execute(cmd)

    def download(self, source, destination):
        cmd = 'docker cp {identifier}:{source} {destination}'.format(
            source=source,
            destination=destination,
            identifier=self.__identifier,
        )
        execute(cmd)

    def execute(self, cmd, timeout=None):
        cmd = 'docker exec -it {identifier} bash -c {cmd}'.format(
            cmd=repr(cmd),
            identifier=self.__identifier
        )
        return execute(cmd, check=False, timeout=timeout)

