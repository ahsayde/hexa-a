from hexaa import HEXAA
import json, os
from flask import session, render_template, request, Markup, send_file
from db.models import User
from requests.exceptions import HTTPError
from tools.tools import *
from tools.http import HttpResponse
from authentication.authenticator import is_authorized
from tools.tools import render_markdown
from minio import Minio, error

hexaa = HEXAA()
app = hexaa._app
config = hexaa._config
http = HttpResponse()

minioconf = config["minio"]
miniocl = Minio(minioconf["url"], minioconf["key"], minioconf["secret"], secure=False)

app.jinja_env.globals.update(timestamp_to_age=timestamp_to_age)
app.jinja_env.globals.update(max=max)
app.jinja_env.globals.update(min=min)
app.jinja_env.globals.update(render_markdown=render_markdown)
app.jinja_env.globals.update(datatimeFromTimestamp=datatimeFromTimestamp)
app.jinja_env.globals.update(dataFromTimestamp=datatimeFromTimestamp)
app.jinja_env.globals.update(get_object_attr=get_object_attr)
app.jinja_env.globals.update(search_for_object=search_for_object)
app.config['UPLOAD_FOLDER'] = config['dirs']['USERS_TMP_CODE_DIR']

@app.errorhandler(HTTPError)
def errors(error):
    status_code = error.response.status_code
    return render_template('errors/{}.html'.format(status_code)), status_code

@app.context_processor
def context_processor():
    userInfo = {}
    if is_authorized():
        userInfo = User.get(username=session['user_id'])
    return dict(userInfo=userInfo)

@app.route("/avatar/<username>")
def GetAvatar(** kwargs):
    username = kwargs.get('username')
    try:
        image = miniocl.get_object("pictures", username)
    except error.NoSuchKey:
        image = "static/photos/default.png"
    return send_file(image, mimetype='image/gif')

if __name__ == '__main__':
    host = config["server"]["host"]
    port = config["server"]["port"]
    app.run(host, port=port, threaded=True)