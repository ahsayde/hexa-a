import json, os, hashlib
from db.models import *
from tools.tools import *
from flask import Blueprint, request, send_file
from werkzeug.utils import secure_filename
from tools.http import HttpResponse
from mongoengine import Q, errors
from authentication.authenticator import hash_password, auth_required

http = HttpResponse()
config = read_config()
users_api = Blueprint('users_api', __name__)

USERS_PROFILE_PHOTOS_DIR = config['dirs']['USERS_PROFILE_PHOTOS_DIR']

@users_api.route("/user")
@auth_required
def GetAuthUser(** kwargs):
    username = kwargs.get('username')
    user = User.get(username=username)
    return http.Ok(json.dumps(user.to_dict()))

@users_api.route("/user/<field>", methods=['PUT'])
@auth_required
def UpdateUserInfo(** kwargs):
    username = kwargs.get('username')
    field = kwargs.get('field')
    timestamp = generate_timestamp()

    user = User.get(username=username)
    if not user:
        return http.NotFound()

    if field not in ['name', 'email', 'password']:
        return http.NotFound()

    credentials = Credentials.get(username=username) 

    if field == 'password':
        old_password = request.json.get('old_password', None)
        new_password = request.json.get('new_password', None)       
        secret = hash_password(old_password, credentials.salt)[0]

        if not secret == credentials.secret:
            return http.BadRequest('Wrong password')
        
        secret, salt = hash_password(new_password)
        try:
            credentials.update(secret=secret, salt=salt, updated_at=timestamp)
        except errors.ValidationError as e:
            return http.BadRequest('Invalid new password')
        except:
            return http.InternalServerError()


    elif field == 'name':
        firstname = request.json.get('firstname', None)
        lastname = request.json.get('lastname', None)
        try:
            user.update(firstname=firstname, lastname=lastname, updated_at=timestamp)
        except errors.ValidationError as e:
            return http.BadRequest()
        except:
            return http.InternalServerError()

    elif field == 'email':
        email = request.json.get('email', None)

        if credentials.get(email=email, username__ne=username):
            return http.Conflict('email already used')
        try:
            credentials.update(email=email, updated_at=timestamp)
            user.update(email=email, updated_at=timestamp)
        except errors.ValidationError as e:
            return http.BadRequest('Invalid emaill address')
        except:
            return http.InternalServerError()

    return http.NoContent()

@users_api.route("/user/picture", methods=['PUT'])
@auth_required
def UpdateUserProfilePicture(** kwargs):
    username = kwargs.get('username')
    picture = request.files.get('picture')
    source_file_name = secure_filename(picture.filename)
    picture_hash = hashlib.md5(username.encode('utf-8')).hexdigest()
    picture.save(os.path.join(USERS_PROFILE_PHOTOS_DIR, picture_hash))
    profile_picture_url = '/avatars/{}'.format(picture_hash)
    User.get(username=username).update(profile_photo=profile_picture_url)
    return http.NoContent()

@users_api.route("/user/picture", methods=['DELETE'])
@auth_required
def DeleteUserProfilePicture(** kwargs):
    username = kwargs.get('username')
    default_photo_url = '/api/avatars/c21f969b5f03d33d43e04f8f136e7682'
    User.get(username=username).update(profile_photo=default_photo_url)
    return http.NoContent()
    
@users_api.route("/user/submissions")
@auth_required
def ListUserSubmmissions(** kwargs):
    username = kwargs.get('username')

    query = {}
    for key in ['group', 'assignment', 'testsuite']:
        value = request.args.get(key, None)
        if value:
            query[key] = value

    submissions = Submission.objects.filter(
        username=username,
        ** query
    )

    data = []
    for submission in submissions:
        temp = submission.to_dict()
        del temp['result']
        data.append(temp)
    
    return http.Ok(json.dumps(data))


@users_api.route("/user/notifications")
@auth_required
def ListUserNotifications(** kwargs):
    username = kwargs.get('username')        
    notifications = Notification.objects.filter(
        to_user=username
    )

    data = []
    for notification in notifications:
        data.append(notification.to_dict())
    
    return http.Ok(json.dumps(data))

@users_api.route("/users/search")
def SearchForUser(** kwargs):
    string = request.args.get('q')
    user = User.objects.filter(username__icontains=string)
    return http.Ok(user.to_json())

@users_api.route("/users/<username>")
def GetUserInfo(** kwargs):
    username = kwargs.get('username')
    user = User.get(username=username)

    if not user:
        return http.NotFound()
    
    return http.Ok(json.dumps(user.to_dict()))
