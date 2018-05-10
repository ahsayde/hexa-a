from client.client import Client
from flask import Blueprint, render_template, session
from authentication.authenticator import login_required, group_access_level

api = Client()
page = 'settings'

settings_page = Blueprint('settings_page', __name__)

@settings_page.before_request
@login_required
def client_auth(**kwargs):
    api.set_auth_header('Bearer %s' % session['jwt'])

@settings_page.route("/groups/<groupId>/settings")
@login_required
@group_access_level('admin')
def SettingsPage(** kwargs):
    groupId = kwargs.get('groupId')
    group = api.groups.get(groupId=groupId).json()
    return render_template('group/settings/settings.html', page=page, group=group)