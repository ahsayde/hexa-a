from client.client import Client
from flask import Blueprint, render_template, session
from authentication.authenticator import login_required, group_access_level

api = Client()
page = 'members'

members_page = Blueprint('members_page', __name__)

@members_page.before_request
@login_required
def client_auth(**kwargs):
    api.set_auth_header('Bearer %s' % session['jwt'])

@members_page.route("/groups/<groupId>/members")
@login_required
@group_access_level('member')
def MembersPage(** kwargs):
    user_role = kwargs.get('user_role')
    username = kwargs.get('username', None)
    groupId = kwargs.get('groupId', None)
    group = api.groups.get(groupId=groupId).json()
    members = api.groups.members.list(groupId=groupId).json()

    requests = []
    if user_role == 'admin':
        requests = api.groups.requests.list(groupId=groupId).json()
        
    return render_template('group/members.html', page=page, group=group, members=members, requests=requests)