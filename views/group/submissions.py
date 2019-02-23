import json
from flask import Blueprint, request, render_template, redirect, session, url_for
from tools.tools import *
from tools.http import HttpResponse
from authentication.authenticator import login_required, logout_required, group_access_level
from client.client import Client
from db.models import *


api = Client()
http = HttpResponse()

page = 'submissions'
submissions_pages = Blueprint('submissions_pages', __name__)

@submissions_pages.before_request
@login_required
def client_auth(**kwargs):
    api.set_auth_header('Bearer %s' % session['jwt'])

@submissions_pages.route("/submissions/<submissionId>")
@login_required
def SubmissionPage(**kwargs):
    username = kwargs.get('username')
    submissionId = kwargs.get('submissionId', None)
    submission = api.groups.submissions.get(submissionId).json()
    group = api.groups.get(submission['group']['uid']).json()    
    return render_template('group/assignment/submission.html', page=page, group=group, submission=submission,)


