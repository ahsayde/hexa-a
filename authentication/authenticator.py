import time, jwt, uuid, hashlib
from functools import wraps
from db.models import *
from tools.tools import *
from authentication.session import SessionManager
from tools.http import HttpResponse
from flask import request, session, redirect
from tools.tools import read_config
from mongoengine import Q, DoesNotExist

http = HttpResponse()
sessionManager = SessionManager()
jwt_secret = read_config()['jwt-secret']

def is_valid_credentials(identifier, password):
    try:
        credentials = Credentials.objects.get(Q(username=identifier) | Q(email=identifier))
    except DoesNotExist:
        return False
    
    secret = hash_password(password, credentials.salt)[0]
    if secret == credentials.secret:
        return True
    else:
        return False

def authorize_user(identifier):
    user = User.objects.get(
        Q(username=identifier) | Q(email=identifier)
    )

    _jwt = generate_jwt(user.username)
    timestamp = generate_timestamp()
    sessionManager.create_session(
        user_id=user.username,
        jwt=_jwt,
        timestamp=timestamp
    )

def logout_user():
    key = session['key']
    sessionManager.destroy_session(key)

def is_authorized():
    if session:
        key = session['key']
        if not sessionManager.is_valid_session(key):
            return False
        else:
            if validate_jwt(session['jwt']):
                return session['user_id']
            else:
                return False

    else:
        auth_header = request.headers.get('AUTH-TOKEN')
        if not auth_header:
            return False

        auth, _jwt = auth_header.split(' ')
        if auth == 'Bearer':
            payload = validate_jwt(_jwt)
            if payload:
                return payload['user_id']
            return False
        else:
            return False

    return False
        

def generate_jwt(user_id):
    timestamp = generate_timestamp() + 8600
    payload = {
        'iss':'hexa-a',
        'user_id':user_id,
        'exp': timestamp
    }

    _jwt = jwt.encode(payload, jwt_secret, algorithm='HS256')
    return _jwt

def validate_jwt(_jwt):
    try:
        payload = jwt.decode(_jwt, jwt_secret, algorithm=['HS256'])
        if payload['exp'] < time.time():
            return False
        else:
            return payload
    except Exception as e:
        return False

def hash_password(password, salt=None):
    salt = salt or uuid.uuid4().hex
    payload = password.encode('utf-8') + salt.encode('utf-8')
    hashed_password = hashlib.sha512(payload).hexdigest()
    return hashed_password, salt

def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        username = is_authorized()
        if not username:
            return redirect('/login?r=' + request.url, code=302)
        
        kwargs['username'] = username
        return func(*args, **kwargs)
    return decorator

def logout_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if is_authorized():
            return redirect('/', code=302)
        return func(*args, **kwargs)
    return decorator

def auth_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        username = is_authorized()
        if not username:
            return http.Unauthorized('Session is expired, please login')

        kwargs['username'] = username
        return func(*args, **kwargs)
    return decorator

def group_access_level(role):
    def group_auth(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            username = kwargs['username']
            groupId = kwargs['groupId']

            if not Group.get(uid=groupId):
                return http.NotFound('Group not found')

            membership = GroupMembership.get(
                user=username,
                group=groupId
            )

            if not membership:
                return http.Forbidden()

            if role == 'admin':
                    if not role == membership.role:
                        return http.Forbidden()

            elif role == 'member':
                if membership.role not in ['admin', 'member']:
                    return http.Forbidden()

            kwargs['user_role'] = membership.role

            return func(*args, **kwargs)
        return decorator
    return group_auth
        
