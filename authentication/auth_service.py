import json, jwt, time
from flask import Blueprint, request
from tools.tools import *
from tools.http import HttpResponse
from authentication.authenticator import is_valid_credentials, is_authorized

http = HttpResponse()
secret = read_config()['jwt-secret']
auth_service = Blueprint('auth_service', __name__)

@auth_service.route("/auth", methods=["POST"])
def authentecation(** kwargs):
    login = request.args.get('login')
    password = request.args.get('password')

    if not is_valid_credentials(login, password):
        return http.Unauthorized()

    payload = {
        'iss':'hexa-a',
        'user_id': login,
        'exp': time.time() + 8600
    }

    token = jwt.encode(payload, secret, algorithm='HS256').decode('utf-8')
        
    return http.Ok(json.dumps({'access_token':token}))

@auth_service.route("/authorized", methods=["GET"])
def is_user_authorized(** kwargs):
    user_id = is_authorized()
    if user_id:
        data = {'authorized':True, 'user_id':user_id}
    else:
        data = {'authorized':False}
        
    return http.Ok(json.dumps(data))
