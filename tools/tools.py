from os import path, mkdir
from datetime import datetime
from flask import Markup
import uuid, time, hashlib, json, yaml, mistune
from subprocess import run, PIPE, TimeoutExpired

def generate_uuid(length=10):
    return str(uuid.uuid4()).replace('-', '')[:length]

def generate_timestamp():
    return int(time.time())

def get_file_extension(filename):
    return filename[filename.rfind('.'):]

def read_config(file='config.yaml'):
    config_path = path.dirname(path.dirname(path.abspath(__file__)))
    with open(file, 'r') as f:
        config =  yaml.load(f)
    return config

def render_markdown(content):
    markdown = mistune.Markdown(escape=True, hard_wrap=True)
    return Markup(markdown(content))

def execute(cmd, timeout=None, check=True):
    try:
        response = run(
            ['bash', '-c', cmd], 
            stdout=PIPE, 
            stderr=PIPE, 
            timeout=timeout, 
            universal_newlines=True
        )
        if check and response.returncode:
            raise RuntimeError(response)
        else:
            return response

    except TimeoutExpired:
        if check:
                raise

def timestamp_to_age(target):
    now = datetime.utcnow()
    target = datetime.utcfromtimestamp(target)
    age = now-target
    if age.days > 365:
        return '{} year ago'.format(int(age.days/360))
    elif age.days > 30:
        return '{} months ago'.format(int(age.days/30))
    elif age.days:
        return '{} days ago'.format(age.days)
    elif age.seconds > 3600:
        return '{} hours ago'.format(int(age.seconds/3600))
    elif age.seconds > 60:
        return '{} minutes ago'.format(int(age.seconds/60))
    else:
        return 'Just now'


def parse_testcases_file(file, username, timestamp):
    content = file.read().decode('utf-')
    lines = content.splitlines()
    if len(lines) % 2 != 0:
        return None

    testcases = []
    for i in range(int(len(lines)/2)):
        testcase = {
            '_id': generate_uuid(5),
            'stdin': lines.pop(0),
            'expected_stdout': lines.pop(0),
            'added_by': username,
            'added_at': timestamp
        }
        testcases.append(testcase)

    return testcases

def datetimeToEpoc(value):
    if not value:
        return None

    try:
        epoc = int(time.mktime(time.strptime(value, "%Y-%m-%dT%H:%M")))
    except:
        return False

    return epoc

def datatimeFromTimestamp(timestamp):
    if not timestamp:
        return None

    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%dT%H:%M')


def get_object_attr(obj, attr):
    return [x[attr] for x in obj] 
