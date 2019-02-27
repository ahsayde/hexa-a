from subprocess import run, PIPE, TimeoutExpired, CompletedProcess
from codes import exitcodes

def _error_decode(response):
    stderr = ""
    if response.returncode:
        if response.returncode < 0:
            errmsg = exitcodes.get(abs(response.returncode), "Unknown Error")
            if isinstance(errmsg, dict):
                errmsg = errmsg["descr"]
        else:
            errmsg = response.stderr
        stderr = "Exit code ({}): {}".format(abs(response.returncode), errmsg)
    return response.returncode, stderr
        
def execute(cmd, workdir=None, timeout=60):
    cmd = ["/bin/bash", "-c", cmd]
    try:
        response = run(
            cmd,
            stderr=PIPE,
            stdout=PIPE,
            cwd=workdir,
            timeout=timeout,
            universal_newlines=True,
        )
    except TimeoutExpired:
        response = CompletedProcess(
            args=cmd,
            returncode=124,
            stderr="Timeout"
        )
    except:
        response = CompletedProcess(
            args=cmd,
            returncode=-1,
            stderr="Internal Checker Error"
        )

    response.stdout = str(response.stdout)
    response.returncode, response.stderr = _error_decode(response)
    return response