from client.client import Client
from flask import Blueprint, request, render_template, session
from authentication.authenticator import login_required, logout_required, group_access_level

api = Client()
user_pages = Blueprint('user_pages', __name__)

@user_pages.before_request
@login_required
def client_auth(**kwargs):
    api.set_auth_header('Bearer %s' % session['jwt'])

@user_pages.route("/dashboard")
@login_required
def DashboardPage(username):
    return render_template('user/dashboard.html')

@user_pages.route("/groups")
@login_required
def GroupsPage(** kwargs):
    groups = api.groups.list().json()
    return render_template('user/groups.html', groups=groups)

@user_pages.route("/settings")
@login_required
def SettingsPage(** kwargs):
    username = kwargs.get('username')
    user = api.users.getUser(username).json()
    return render_template('user/settings.html', user=user)