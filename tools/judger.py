import json
from tools.sandbox import Sandbox
from tools.exit_codes import exit_codes_table

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
        cmd = "bash -c 'g++ -w -fmessage-length=10000 -fno-diagnostics-show-caret -fdiagnostics-color=never -std=c++98 *.cpp -o output.out'"
        compiler_result = self._sandbox.execute(self.container.id, cmd)
        self.result['compiler'] = compiler_result

    def __run_test(self, stdin, timeout=5):
        cmd = 'timeout {}s ./output.out {}'.format(timeout, stdin)    
        return self._sandbox.execute(self.container.id, cmd)
        
    def runTests(self, testcases):
        passed_tests = failed_tests = errored_tests = 0

        for testcase in testcases:
            expected_stdout = bytes(testcase['expected_stdout'], encoding='ascii')
            expected_stdout = expected_stdout.decode('unicode-escape')

            try:
                output = self.__run_test(testcase['stdin'])
                error_code = int(output['returncode'])

                if error_code:
                    status = 'Errored'
                    errored_tests += 1

                    if error_code > 128:
                        error_code = int(error_code) - 128

                    error_code = exit_codes_table.get(error_code)

                    if error_code:    
                        testcase['stderr'] = "{} - {}".format(error_code['name'], error_code['descr'])  
                    else:
                        testcase['stderr'] = 'Unknown error'                                          
                else:
                    if expected_stdout.strip() == output['output'].strip():
                        status = 'Passed'
                        passed_tests += 1
                    else:
                        status = 'Failed'
                        failed_tests += 1

                    testcase['stderr'] = None
                
                testcase['stdout'] = repr(output['output'])
                testcase['status'] = status
                testcase['returncode'] = output['returncode']
                testcase['expected_stdout'] = repr(expected_stdout)
                
            except:
                testcase['returncode'] = 'N/A'
                testcase['stdout'] = 'N/A'
                testcase['stderr'] = 'Unexpected Server Error'
                testcase['status'] = "Errored"
                testcase['expected_stdout'] = repr(expected_stdout)

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

   