import unittest
from tools.sandbox import Sandbox
from tools.tools import read_config, get_file_extension

class Testcase(unittest.TestCase):
    def __init__(self, **kwargs):
        super(Testcase, self).__init__()
        self.stdin = kwargs.get('stdin', None)
        self.expected_stdout = kwargs.get('expected_stdout', None)

        Testcase.docker_image = kwargs.get('docker_image')
        Testcase.source_file = kwargs.get('source_file')
        Testcase.reference_id = kwargs.get('reference_id')
        Testcase.exec_command = kwargs.get('exec_command')
        
    @classmethod
    def setUpClass(cls):
        cls.__container = Sandbox().create(cls.docker_image)
        cls.__container.start()

        source_file_path = '/tmp/hexa-a/{}/{}'.format(
            cls.reference_id,
            cls.source_file
        )

        cls.__container.upload(source_file_path)

    def runTest(self):
        cmd = self.exec_command.format(stdin=self.stdin, source_file=self.source_file)
        response = self.__container.execute(cmd=cmd, timeout=3)
        self.stdout = response.stdout.strip()
        self.returncode = response.returncode 

        self.assertEqual(self.returncode, 0)  
        self.assertEqual(self.stdout, self.expected_stdout)

    @classmethod
    def tearDownClass(cls):
        cls.__container.remove()


class TestSuiteResult(unittest.TextTestResult):
    def __init__(self, stream=None, descriptions=None, verbosity=0):
        super(TestSuiteResult, self).__init__(stream, descriptions, verbosity)
        
    def addError(self, test, err):
        self.saveTestCaseResult(test, 'Errored', err)
        return super(TestSuiteResult, self).addError(test, err)

    def addFailure(self, test, err):
        self.saveTestCaseResult(test, 'Failed', err)
        return super(TestSuiteResult, self).addFailure(test, err)

    def addSuccess(self, test):
        self.saveTestCaseResult(test, 'Passed')
        return super(TestSuiteResult, self).addSuccess(test)

    def saveTestCaseResult(self, test, status, err=None):
        if status == 'Errored':
            self.result.append(
                {
                    'status': 'Errored',
                    'details': err
                }
            )
        else:
            self.result.append(
                {
                    'stdin':repr(test.stdin),
                    'stdout':repr(test.stdout),
                    'returncode': repr(test.returncode),
                    'expected_stdout':repr(test.expected_stdout),
                    'status':repr(status)
                }
            )


class Judger:
    def __init__(self, language, reference_id, source_file):
        self.language = language
        self.source_file = source_file
        self.reference_id = reference_id
        self.TestSuite = unittest.TestSuite()
        self.TestResult = TestSuiteResult()
        self.TestResult.result = []

    def setTestsuite(self, testsuite):
        for testcase in testsuite.testcases:
            testcase_object = Testcase(
                stdin=testcase.stdin, 
                expected_stdout=testcase.expected_stdout,
                reference_id=self.reference_id,
                source_file=self.source_file,
                docker_image=self.language['docker-image'],
                exec_command=self.language['exec']
            )
            self.TestSuite.addTest(testcase_object)
        
    def runTest(self):
        self.TestSuite.run(self.TestResult)
        return self.TestResult.result