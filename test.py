from tools.sandbox import Sandbox
from tools.tools import read_config
import mongoengine
from db.models import Testsuite

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
        
        if not compiler_status:
            return self.result

        self.__runTests(testsuite)

        self.__teardown()

    def __setup(self, source_path, source_file):
        self._container = Sandbox().create(self.docker_image)
        self._container.start()
        source_file_path = source_path + '/' + source_file
        self._container.upload(source_file_path)

    def __compile(self, source_file):
        cmd = self.compiler['cmd'].format(source_file=source_file)
        output = self._container.execute(cmd=cmd, timeout=3)

        self.result['compiler'] = {
            'returnecode': output.returncode,
            'stdout': output.stdout,
            'stderr': output.stderr
        }

        return not bool(output.returncode)

    def __runTests(self, testsuite):
        passed_tests = 0
        failed_tests = 0
        errored_tests = 0

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
                    'stderr': response.stderr,
                    'status': status
                }
            )

        self.result['summary'] = {
            'passed': passed_tests,
            'failed': failed_tests,
            'errored': errored_tests
        }

        return True
    
    def __teardown(self):
        self._container.remove()
            

config = read_config('judger_config.yaml')['languages']['cpp_98']
mongoengine.connect(db='hexa-a-db', host='127.0.0.1', port=2000)
testsuite = Testsuite.get(_id='bfce613cc8')
source_path = '/tmp/hexa-a/123'
source_file = 'main.cpp'

jj = Judger(config)
r = jj.judge(source_path, source_file, testsuite)

print(jj.result)

# import unittest
# from tools.sandbox import Sandbox
# from tools.tools import read_config, get_file_extension
# from db.models import Testsuite
# import mongoengine

# class Testcase(unittest.TestCase):
#     def __init__(self, **kwargs):
#         super(Testcase, self).__init__()
#         self.stdin = kwargs.get('stdin', None)
#         self.expected_stdout = kwargs.get('expected_stdout', None)
#         # configration
#         Testcase.docker_image = kwargs.get('docker_image')
#         Testcase.source_file = kwargs.get('source_file')
#         Testcase.exec_command = kwargs.get('exec_command')
        
#     @classmethod
#     def setUpClass(cls):
#         cls.__container = Sandbox().create(cls.docker_image)
#         cls.__container.start()
#         cls.__container.upload(cls.source_file)

#     def runTest(self):
#         cmd = self.exec_command.format(stdin=self.stdin, source_file=self.source_file)
#         response = self.__container.execute(cmd=cmd, timeout=3)
#         self.stdout = response.stdout.strip()
#         self.returncode = response.returncode 

#         self.assertEqual(self.returncode, 0)  
#         self.assertEqual(self.stdout, self.expected_stdout)

#     @classmethod
#     def tearDownClass(cls):
#         cls.__container.remove()


# class TestSuiteResult(unittest.TextTestResult):
#     def __init__(self, stream=None, descriptions=None, verbosity=0):
#         super(TestSuiteResult, self).__init__(stream, descriptions, verbosity)
        
#     def addError(self, test, err):
#         self.saveTestCaseResult(test, 'Errored', err)
#         return super(TestSuiteResult, self).addError(test, err)

#     def addFailure(self, test, err):
#         self.saveTestCaseResult(test, 'Failed', err)
#         return super(TestSuiteResult, self).addFailure(test, err)

#     def addSuccess(self, test):
#         self.saveTestCaseResult(test, 'Passed')
#         return super(TestSuiteResult, self).addSuccess(test)

#     def saveTestCaseResult(self, test, status, err=None):
#         if status == 'Errored':
#             self.result.append(
#                 {
#                     'error': 'Internal server error',
#                     'details': err
#                 }
#             )
#         else:
#             self.result.append(
#                 {
#                     'stdin':repr(test.stdin),
#                     'stdout':repr(test.stdout),
#                     'returncode': repr(test.returncode),
#                     'expected_stdout':repr(test.expected_stdout),
#                     'status':repr(status)
#                 }
#             )


# class Judger:
#     def __init__(self, language, source_file, sandbox):
#         self.language = language
#         self.source_file = source_file
#         self.sandbox = sandbox
#         self.TestSuite = unittest.TestSuite()
#         self.TestResult = TestSuiteResult()
#         self.TestResult.result = []

#     def setTestsuite(self, testsuite):
#         for testcase in testsuite.testcases:
#             testcase_object = Testcase(
#                 stdin=testcase.stdin, 
#                 expected_stdout=testcase.expected_stdout,
#                 source_file=self.source_file,
#                 sandbox=self.sandbox,
#                 exec_command=self.language['exec']
#             )
#             self.TestSuite.addTest(testcase_object)
        
#     def runTest(self):
#         self.TestSuite.run(self.TestResult)
#         return self.TestResult.result

# language = read_config('judger_config.yaml')['languages']['python_3.5']

# mongoengine.connect(db='hexa-a-db', host='127.0.0.1', port=2000)
# testsuite = Testsuite.get(_id='e57b571264')
# jj = Judger(source_file='main.py', reference_id='123', language=language)
# jj.setTestsuite(testsuite)
# result = jj.runTest()
# print(result)



# # import unittest
# # from tools.sandbox import Sandbox
# # from tools.tools import read_config, get_file_extension

# # class Testcase(unittest.TestCase):
# #     def __init__(self, stdin, expected_stdout):
# #         super(Testcase, self).__init__()
# #         self.stdin = stdin
# #         self.expected_stdout = expected_stdout

# #     @classmethod
# #     def setUpClass(cls):
# #         cls.__container = Sandbox().create('python:3.5')
# #         cls.__container.start()
# #         cls.__container.upload('/tmp/hexa-a/main.py')

# #     def runTest(self):
# #         cmd = 'python main.py {stdin}'.format(stdin=self.stdin)
# #         response = self.__container.execute(cmd=cmd, timeout=3)
# #         self.stdout = response.stdout.strip()
# #         self.returncode = response.returncode 

# #         self.assertEqual(self.returncode, 0)  
# #         self.assertEqual(self.stdout, self.expected_stdout)

# #     @classmethod
# #     def tearDownClass(cls):
# #         cls.__container.remove()


# # class TestSuiteResult(unittest.TextTestResult):
# #     def __init__(self, stream=None, descriptions=None, verbosity=0):
# #         print('testresult')
# #         super(TestSuiteResult, self).__init__(stream, descriptions, verbosity)
        
# #     # def addError(self, test, err):
# #     #     self.saveTestCaseResult(test, 'Errored')
# #     #     return super(TestSuiteResult, self).addError(test, err)

# #     # def addFailure(self, test, err):
# #     #     self.saveTestCaseResult(test, 'Failed')
# #     #     return super(TestSuiteResult, self).addFailure(test, err)

# #     # def addSuccess(self, test):
# #     #     self.saveTestCaseResult(test, 'Passed')
# #     #     return super(TestSuiteResult, self).addSuccess(test)

# #     # def saveTestCaseResult(self, test, status):
# #     #     if test.TestSuiteName not in self.result:
# #     #         self.result[test.TestSuiteName] = []

# #     #     self.result[test.TestSuiteName].append(
# #     #         {
# #     #             'stdin':repr(test.stdin),
# #     #             'stdout':repr(test.stdout),
# #     #             'returncode': repr(test.returncode),
# #     #             'expected_stdout':repr(test.expected_stdout),
# #     #             'status':repr(status)
# #     #         }
# #     #     )


# # testsuites = [
# #     {
# #         'name':'testsuite1',
# #         'testcases':[
# #             {
# #                 'stdin':'1',
# #                 'expected_stdout':'1'
# #             },
# #             {
# #                 'stdin':'2',
# #                 'expected_stdout':'2'
# #             }
# #         ]
# #     },
# #     {
# #         'name':'testsuite2',
# #         'testcases':[
# #             {
# #                 'stdin':'3',
# #                 'expected_stdout':'3'
# #             },
# #             {
# #                 'stdin':'4',
# #                 'expected_stdout':'4'
# #             }
# #         ]
# #     }
# # ]

# # class Judger:
# #     def __init__(self):
# #         self.testsuites_list = []
# #         self.TestResult = TestSuiteResult()
# #         self.TestResult.result = {}

# #     def addTestsuite(self, testsuite_dict):
# #         TestSuite = unittest.TestSuite()
# #         testcases_list = []
# #         for testcase in testsuite_dict['testcases']:
# #             TestCase = Testcase(testcase['stdin'], testcase['expected_stdout'])
# #             TestCase.TestSuiteName = testsuite_dict['name']
# #             testcases_list.append(TestCase)
        
# #         TestSuite.addTests(testcases_list)
# #         self.testsuites_list.append(TestSuite)

# #     def runTest(self):
# #         Tests = unittest.TestSuite(self.testsuites_list)
# #         Tests.run(self.TestResult)
# #         return self.TestResult.result




# # testresult = TestSuiteResult()
# # testsuite = unittest.TestSuite()
# # testsuite.addTest(Testcase(1,1))
# # testsuite.run(testresult)
# # print(testresult)


# # # jj = Judger()

# # # for testsuite in testsuites:
# # #     jj.addTestsuite(testsuite)

# # # result = jj.runTest()

# # # print(result)
















# #     # def addTestcase(self, testcase):
# #     #     testCaseObj = Testcase(testcase['stdin'], testcase['expected_stdout'])
# #     #     testCaseObj.TestSuiteName = testsuite['name']

# #     #     testcases_object_list.append(testcase_object)

# #     # def runTests(self):
        

# # # test_result_object = TestSuiteResult()
# # # test_result_object.results = {}

# # # testsuites_object_list = []
# # # for testsuite in testsuites:
# # #     testcases_object_list = []
# # #     testsuite_object = unittest.TestSuite()

# # #     for testcase in testsuite['testcases']:
# # #         testcase_object = Testcase(testcase['stdin'], testcase['expected_stdout'])
# # #         testcase_object.TestSuiteName = testsuite['name']
# # #         testcases_object_list.append(testcase_object)
    
# # #     testsuite_object.addTests(testcases_object_list)
# # #     testsuites_object_list.append(testsuite_object)
        
# # # tests_object = unittest.TestSuite(testsuites_object_list)
# # # tests_object.run(test_result_object)

# # # print(test_result_object.results)
