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

@submissions_pages.route("/groups/<groupId>/submissions")
@login_required
@group_access_level('member')
def SubmissionsPage(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId', None)
    
    group = Group.get(uid=groupId)
    if not group:
        return http.NotFound()

    group = group.to_dict()

    membership = GroupMembership.get(group=groupId, user=username)
    if not membership:
        return http.Forbidden()
    
    query = {}
    submissions = []

    members = api.groups.members.list(groupId).json()
    assignments = api.groups.assignments.list(groupId).json()
    testsuites = api.groups.testsuites.list(groupId).json()

    if membership.role == 'admin':
        allowed_filter_keys = ['username', 'assignment', 'testsuite']
        group['is_admin'] = True
    
    elif membership.role == 'member':
        allowed_filter_keys = ['assignment', 'testsuite']

    for key in allowed_filter_keys:
        value = request.args.get(key, None)
        if value:
            if key == 'assignment':
                query[key] = Assignment.get(group=groupId, name=value)
            elif key == 'testsuite':
                query[key] = Testsuite.get(group=groupId, name=value)
            else:
                query[key] = value
    
    if membership.role == 'admin':
        submissions = Submission.objects(group=groupId, **query)

    elif membership.role == 'member':
        submissions = Submission.objects(group=groupId, username=username, **query)

    return render_template(
        'group/assignment/submissions.html', 
        page=page, 
        group=group,
        members=members,
        assignments=assignments,
        testsuites=testsuites,
        submissions=submissions,
        filters=request.args
    )

@submissions_pages.route("/submissions/<submissionId>")
@login_required
def SubmissionPage(**kwargs):
    username = kwargs.get('username')
    submissionId = kwargs.get('submissionId', None)
    submission = api.groups.submissions.get(submissionId).json()
    return render_template('group/assignment/submission.html', page=page, submission=submission,)


