import json, zipfile, argparse
from importlib.machinery import SourceFileLoader
from os import path, environ, listdir
from judger import Judger

class Checker:
    def __init__(self, workdir, language, sourcefile, testfile):
        self._path = path.dirname(path.abspath(__file__))
        self.workdir = workdir
        self.language = language
        self.sourcefile = sourcefile
        self.testfile = testfile
        self.tmpltdir = path.join(self._path, "templates") 
        self.judger = Judger()

    @property
    def testcases(self):
        testpath = path.join(self.workdir, self.testfile)
        with open(testpath, "r") as f:
            return json.load(f)

    @property
    def languages(self):
        return listdir(self.tmpltdir)

    def _loadModule(self):
        tmpltpath = path.join(self.tmpltdir, self.language)
        loader = SourceFileLoader(self.language, tmpltpath)
        module = loader.load_module()
        module.workdir = self.workdir
        return module

    def check(self):
        if self.language not in self.languages:
            raise ValueError("Language %s is not supported" % self.language)
                
        module = self._loadModule()
        codepath = path.join(self.workdir, self.sourcefile)
        if zipfile.is_zipfile(codepath):
            with zipfile.ZipFile(codepath, "r") as zpf:
                zpf.extractall(self.workdir)
            self.sourcefile = zpf.namelist()

        self.judger.judge(module, self.sourcefile, self.testcases, timeout=3)
        return self.judger.result

    def _export_result(self, results):
        with open(path.join(self.workdir, "result.json"), "w") as f:
            json.dump(results, f)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workdir", type=str, default=environ.get("WORK_DIR", "/data"), help="working directory")
    parser.add_argument("-l", "--language", type=str, default=environ.get("PRO_LANGUAGE"), help="test file")
    parser.add_argument("-s", "--sourcefile", type=str, default=environ.get("SOURCE_FILE"), help="source code file")
    parser.add_argument("-t", "--testfile", type=str, default=environ.get("TEST_FILE"), help="test file")
    args = parser.parse_args()
    checker =  Checker(args.workdir, args.language, args.sourcefile, args.testfile)
    results = checker.check()
    checker._export_result(results)