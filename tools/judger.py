import json
from tools.sandbox import Sandbox

class Judger:
    def __init__(self, reference_id):
        self._sandbox = Sandbox() 
        self.reference_id = reference_id           
        self.result = {'compiler':{}, 'testcases':[], 'summary':{}}

    def _setup(self):
        self.container = self._sandbox.create(user_path=self.reference_id)
        self.container.start()

    def _teardown(self):
        self._sandbox.remove(self.container.id)

    def compile(self):
        cmd = "bash -c 'g++ -w -fmessage-length=10000 -fno-diagnostics-show-caret -std=c++98 *.cpp -o output.out'"
        compiler_result = self._sandbox.execute(self.container.id, cmd)
        self.result['compiler'] = compiler_result
        
    def runTests(self, testcases):
        passed_tests = failed_tests = errored_tests = 0

        for testcase in testcases:
            try:
                testcase['expected_stdout'] = bytes(testcase['expected_stdout'], encoding='ascii').decode('unicode-escape')
                cmd = './output.out {}'.format(testcase['stdin'])    
                output = self._sandbox.execute(self.container.id, cmd)

                if output['returncode']:
                    testcase['returncode'] = output['returncode']
                    testcase['stderr'] = output['output'],                   
                    testcase['stdout'] = None
                    testcase['status'] = 'Failed'
                    testcase['expected_stdout'] = repr(testcase['expected_stdout'])
                    failed_tests += 1

                else:
                    if testcase['expected_stdout'].strip() == output['output'].strip():
                        status = 'Passed'
                        passed_tests += 1
                    else:
                        status = 'Failed'
                        failed_tests += 1
                
                    testcase['returncode'] = output['returncode']
                    testcase['stdout'] = repr(output['output'])
                    testcase['expected_stdout'] = repr(testcase['expected_stdout'])
                    testcase['stderr'] = None                    
                    testcase['status'] = status

            except:
                testcase['returncode'] = 'N/A'
                testcase['stdout'] = 'N/A'
                testcase['expected_stdout'] = repr(testcase['expected_stdout'])
                testcase['stderr'] = 'Unexpected error'
                testcase['status'] = "Errored"

            self.result['testcases'].append(testcase)

        self.result['summary'] = {
            'passed': passed_tests,
            'failed': failed_tests,
            'errored': errored_tests,
            'all':len(testcases)
        }


    def judge(self, testcases):
        self._setup()
        try:
            self.compile()
            self.runTests(testcases)
        except:
            raise
        finally:
            self._teardown()
        
        return self.result

   