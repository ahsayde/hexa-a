import shutil
from tools.sandbox import Sandbox
from tools.tools import read_config

class Judger:
    def __init__(self, config):
        self.docker_image = config.get('docker-image')
        self.executer = config.get('executer')         
        self.compiler = config.get('compiler', None)

    def judge(self, source_path, source_file, testsuite):
        self.result = {'compiler':{}, 'testcases':[], 'summary':{}}
        
        self.__setup(source_path, source_file)

        if self.compiler:
            compiler_status = self.__compile(source_file)
        
        if compiler_status:
            self.__runTests(testsuite)

        self.__teardown(source_path)

    def __setup(self, source_path, source_file):
        self._container = Sandbox().create(self.docker_image)
        self._container.start()
        source_file_path = source_path + '/' + source_file
        self._container.upload(source_file_path)

    def __compile(self, source_file):
        cmd = self.compiler['cmd'].format(source_file=source_file)
        output = self._container.execute(cmd=cmd, timeout=3)

        self.result['compiler'] = {
            'returncode': output.returncode,
            'stdout': output.stdout,
            'stderr': output.stderr
        }

        return not bool(output.returncode)

    def __runTests(self, testsuite):
        passed_tests = 0
        failed_tests = 0
        errored_tests = 0
        # import ipdb; ipdb.set_trace()
        for testcase in testsuite.testcases:
            cmd = self.executer['cmd'].format(stdin=testcase.stdin)
            response = self._container.execute(cmd=cmd, timeout=3)

            if response.returncode:
                status = 'Errored'
                errored_tests += 1
                
            else:
                if testcase.expected_stdout == response.stdout:
                    status = 'Passed'
                    passed_tests += 1
                else:
                    status = 'Failed'
                    failed_tests += 1
            
            self.result['testcases'].append(
                {
                    'returncode': response.returncode,
                    'stdin': testcase.stdin,
                    'stdout': response.stdout,
                    'expected_stdout': testcase.expected_stdout,
                    'stderr': response.stderr,
                    'status': status
                }
            )

        self.result['summary'] = {
            'passed': passed_tests,
            'failed': failed_tests,
            'errored': errored_tests,
            'all':len(testsuite.testcases)
        }

        return True
    
    def __teardown(self, source_path):
        self._container.remove()
        shutil.rmtree(source_path)