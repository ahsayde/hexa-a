import unittest, traceback
from codes import exit_codes

class TestcaseError(BaseException):
    pass


class TestResult(unittest.TextTestResult):
    def __init__(self, stream=None, descriptions=None, verbosity=0):
        super(TestResult, self).__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.failures_count = 0
        self.errors_count = 0
        self.result = []

    def addError(self, test, error):
        self.errors_count += 1
        self.saveTestCaseResult(test, "errored", error)
        return super(TestResult, self).addError(test, error)

    def addFailure(self, test, error):
        self.failures_count += 1
        self.saveTestCaseResult(test, "failed", error)
        return super(TestResult, self).addFailure(test, error)

    def addSuccess(self, test):
        self.success_count += 1
        self.saveTestCaseResult(test, "passed")
        return super(TestResult, self).addSuccess(test)

    def saveTestCaseResult(self, test, status, error=None):
        result = {
            "uid": test.testcase["uid"],
            "status": status,
            "stdin": repr(test.testcase["stdin"]),
            "stdout": repr(test.testcase["expected_stdout"]),
            "stderr": getattr(test, "stderr", ""),
            "generated_stdout": repr(getattr(test, "generated_stdout", "")),
        }

        if error:
            error = "".join(traceback.format_exception_only(error[0], error[1])).strip()
            result["error"] = error

        self.result.append(result)


class TestCase(unittest.TestCase):
    def __init__(self, module, testcase, timeout=None):
        unittest.TestCase.__init__(self)
        self.module = module
        self.testcase = testcase
        self.timeout = timeout

    def runTest(self):
        response = self.module.runTest(
            stdin=self.testcase["stdin"], timeout=self.timeout
        )

        if response.returncode:
            exitcode = response.returncode
            if response.returncode > 128:
                exitcode -= 128
            
            errmsg = exit_codes.get(exitcode, "Unknown Error")
            self.stderr = "Exit code ({}): {}".format(exitcode, errmsg)
            self.fail(self.stderr)
       
        stdout = str(self.testcase["expected_stdout"]).strip()
        self.generated_stdout = str(response.stdout).strip()

        if self.generated_stdout != stdout:
            raise AssertionError(
                "{} != {}".format(repr(self.generated_stdout), repr(stdout))
            )

class Judger:
    def __init__(self):
        self.testresult = TestResult()
        self.testsuite = unittest.TestSuite()

    def _create_testsuite(self, module, testcases, timeout):
        for testcase in testcases:
            obj = TestCase(module=module, testcase=testcase, timeout=timeout)
            self.testsuite.addTest(obj)

    def judge(self, module, sourcefile, testcases, timeout=10):
        self.result = {"tests": [], "compiler": {}, "summary": {}}

        if hasattr(module, "compile"):
            compiler = module.compile(sourcefile, timeout=timeout)
            self.result["compiler"] = {
                "returncode": compiler.returncode,
                "error": compiler.stderr,
            }
            if compiler.returncode:
                self.result["summary"]["status"] = "Compiler Error"
                return

        self._create_testsuite(module=module, testcases=testcases, timeout=timeout)
        self.testsuite.run(self.testresult)

        status = (
            "Failed"
            if (self.testresult.failures_count or self.testresult.errors_count)
            else "Passed"
        )

        self.result.update(
            {
                "tests": self.testresult.result,
                "summary": {
                    "success": self.testresult.success_count,
                    "failures": self.testresult.failures_count,
                    "errors": self.testresult.errors_count,
                    "status": status,
                },
            }
        )
