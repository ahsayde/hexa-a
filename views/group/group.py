from client.client import Client
from flask import Blueprint, render_template, session, redirect
from authentication.authenticator import login_required, group_access_level

api = Client()
page = 'group'

group_pages = Blueprint('group_pages', __name__)

@group_pages.before_request
@login_required
def client_auth(**kwargs):
    api.set_auth_header('Bearer %s' % session['jwt'])

@group_pages.route("/groups/<groupId>")
@login_required
def GroupPage(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    group = api.groups.get(groupId=groupId).json()

    if group['is_admin'] or group['is_member']:
        return redirect('/groups/' + groupId + '/announcements')

    return render_template('group/guest_group_page.html', group=group)
