from os import path, mkdir, getcwd
from datetime import datetime
from flask import Markup
import uuid, time, hashlib, json, yaml, mistune
from subprocess import run, PIPE, TimeoutExpired
from email.mime.text import MIMEText
import smtplib, math

def generate_uuid(length=10):
    return str(uuid.uuid4()).replace('-', '')[:length]

def generate_timestamp():
    return int(time.time())

def get_file_extension(filename):
    return filename[filename.rfind('.'):]

def read_config(file='config.yaml'):
    config_path = getcwd() + '/' + file
    with open(config_path, 'r') as f:
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
            'uid': generate_uuid(5),
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

    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M')

def dataFromTimestamp(timestamp):
    if not timestamp:
        return None

    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')

def get_object_attr(obj, attr):
    return [x[attr] for x in obj] 

def search_for_object(objList, key, value):
    obj = [x for x in objList if x[key] == value] 
    if obj:
        return obj[0]
    
    return None

def send_email(fromaddr, toaddr, body, subject, password):
    config = read_config()['smtp']
    msg = MIMEText(body)
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    server = smtplib.SMTP_SSL(config['host'], config['port'])
    server.login(fromaddr, password)

    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def pagenate(limit, page, count, request_url):
    base_url = request_url[:request_url.find('?')]
    pages = math.ceil(count/limit)
    page = min(pages, page)
        
    if page < pages:
        next_page = page + 1
    else:
        next_page = None

    if page > 1:
        prev_page = page - 1
    else:
        prev_page = None

    pagenation = {
        'count': count,
        'limit': limit,
        'current_page': page,
        'pages': pages,
        'next_page': next_page,
        'prev_page': prev_page 
    }

    return pagenation

# def pagenate(limit, offset, count, request_url):

#     base_url = request_url[:request_url.find('?')]
#     pages = math.ceil(count/limit)
#     current_page = math.floor(offset / limit) + 1
#     current_page = min(pages, current_page)

#     if (offset + limit) < count:
#         next_url = '{0}?limit={1}&offset={2}'.format(base_url, limit, offset + limit)
#     else:
#         next_url = None

#     if (offset - limit) >= 0:
#         prev_url = '{0}?limit={1}&offset={2}'.format(base_url, limit, offset - limit)
#     else:
#         prev_url = None

#     pagenation = {
#         'limit': limit,
#         'offset': offset,
#         'count': count,
#         'pages': pages,
#         'current_page': current_page,
#         'self_url': request_url,
#         'next_url': next_url,
#         'prev_url': prev_url 
#     }

#     return pagenation
