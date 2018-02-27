import json
from tools.sandbox import Sandbox

class Judger:
    def __init__(self, reference_id, config):
        self._sandbox = Sandbox() 
        self.config = config
        self.reference_id = reference_id           
        self.result = {'compiler':{}, 'testcases':[], 'summary':{}}

    def _setup(self):
        self.container = self._sandbox.create(user_path=self.reference_id, environment=self.config)
        self.container.start()

    def _teardown(self):
        self._sandbox.remove(self.container.id)

    def compile(self):
        compiler_result = self._sandbox.execute(self.container.id, 'python3 /opt/hexa-checker.py compile')
        self.result['compiler'] = json.loads(compiler_result['stdout'])
        
    def runTests(self):
        test_result = self._sandbox.execute(self.container.id, 'python3 /opt/hexa-checker.py runtests')
        self.result['testcases'] = json.loads(test_result['stdout'])['testcases']
        self.result['summary'] = json.loads(test_result['stdout'])['summary']

    def judge(self):
        self._setup()
        try:
            self.compile()
            self.runTests()
        except:
            raise
        finally:
            self._teardown()
        
        return self.result

   