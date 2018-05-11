from client.client import Client
from flask import Blueprint, render_template, session
from authentication.authenticator import login_required, group_access_level

api = Client()
page = 'announcements'

announcements_pages = Blueprint('announcements_pages', __name__)

@announcements_pages.before_request
@login_required
def client_auth(**kwargs):
    api.set_auth_header('Bearer %s' % session['jwt'])

@announcements_pages.route("/groups/<groupId>/announcements")
@login_required
@group_access_level('member')
def AnnouncementsPage(** kwargs):
    groupId = kwargs.get('groupId')
    group = api.groups.get(groupId=groupId).json()
    announcements = api.groups.announcements.list(groupId).json()
    return render_template('group/announcement/announcements.html', page=page, group=group, announcements=announcements)

