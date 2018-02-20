from hexaa import HEXAA
import json, os
from flask import session, render_template, request, Markup, send_file
from db.models import User, Notification
from requests.exceptions import HTTPError
from tools.tools import *
from tools.http import HttpResponse
from authentication.authenticator import is_authorized
from tools.tools import render_markdown

hexaa = HEXAA()
app = hexaa._app
config = hexaa._config
http = HttpResponse()

app.jinja_env.globals.update(timestamp_to_age=timestamp_to_age)
app.jinja_env.globals.update(render_markdown=render_markdown)
app.jinja_env.globals.update(datatimeFromTimestamp=datatimeFromTimestamp)
app.jinja_env.globals.update(get_object_attr=get_object_attr)
app.jinja_env.globals.update(search_for_object=search_for_object)

USERS_PROFILE_PHOTOS_DIR = config['dirs']['USERS_PROFILE_PHOTOS_DIR']
app.config['UPLOAD_FOLDER'] = config['dirs']['USERS_TMP_CODE_DIR']

@app.errorhandler(HTTPError)
def errors(error):
    status_code = error.response.status_code
    return render_template('errors/{}.html'.format(status_code)), status_code

@app.context_processor
def context_processor():
    userInfo = {}
    notifications = []
    if is_authorized():
        userInfo = User.get(username=session['user_id'])
        notifications = Notification.objects(to_user=userInfo.username)
    return dict(userInfo=userInfo, notifications=notifications)

@app.route("/avatars/<avatarId>")
def GetAvatar(** kwargs):
    avatarId = kwargs.get('avatarId')    
    local_picture_path = os.path.join(USERS_PROFILE_PHOTOS_DIR, avatarId)
    if not os.path.exists(local_picture_path):
        return http.NotFound()
    return send_file(local_picture_path, mimetype='image/gif')

if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)

