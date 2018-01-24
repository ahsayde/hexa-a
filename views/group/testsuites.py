from client.client import Client
from flask import Blueprint, render_template, session
from authentication.authenticator import login_required, group_access_level

api = Client()
page = 'testsuites'

testsuites_pages = Blueprint('testsuites_pages', __name__)

@testsuites_pages.before_request
@login_required
def client_auth(**kwargs):
    api.set_auth_header('Bearer %s' % session['jwt'])

@testsuites_pages.route("/groups/<groupId>/testsuites")
@login_required
@group_access_level('member')
def TestsuitesPage(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    group = api.groups.get(groupId=groupId).json()
    testsuites = api.groups.testsuites.list(groupId).json()
    return render_template('group/testsuites.html', page=page, group=group, testsuites=testsuites)

@testsuites_pages.route("/groups/<groupId>/testsuites/<testsuiteId>")
@login_required
@group_access_level('member')
def TestsuitePage(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    testsuiteId = kwargs.get('testsuiteId')
    group = api.groups.get(groupId=groupId).json()
    testsuite = api.groups.testsuites.get(groupId, testsuiteId).json()
    suggested_testcases = api.groups.testsuites.getSuggestedTestcases(groupId, testsuiteId).json()
    return render_template('group/testsuite.html', page=page, group=group, testsuite=testsuite, suggested_testcases=suggested_testcases)


