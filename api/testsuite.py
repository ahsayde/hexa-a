import json
from flask import Blueprint, request
from db.models import *
from tools.tools import *
from tools.http import HttpResponse
from authentication.authenticator import auth_required, group_access_level

http = HttpResponse()
testsuites_api = Blueprint('testsuites_api', __name__)

@testsuites_api.route("/testsuites")
@auth_required
@group_access_level('members')
def ListTestsuites(** kwargs):
    limit = request.args.get('limit', 25, int)
    page = request.args.get('page', 1, int) or 1
    offset = (page - 1) * limit

    user_role = kwargs.get('user_role')
    groupId = kwargs.get('groupId')

    if user_role == 'member':
        count = Testsuite.objects(group=groupId, public=True).count()
        requested_testsuites = Testsuite.objects(
            group=groupId, 
            public=True
        ).exclude('testcases').limit(limit).skip(offset)

    elif user_role == 'admin':
        count = Testsuite.objects(group=groupId).count()
        requested_testsuites = Testsuite.objects(
            group=groupId
        ).exclude('testcases').limit(limit).skip(offset)

    testsuites = []
    for testsuite in requested_testsuites:
        testsuites.append(testsuite.to_dict())

    pagenation = pagenate(limit, page, count, request.url)

    data = {
        'pagenation': pagenation,
        'result': testsuites
    }

    return http.Ok(json.dumps(data))
    
@testsuites_api.route("/testsuites/<testsuiteId>")
@auth_required
@group_access_level('members')
def GetTestsuiteInfo(** kwargs):
    user_role = kwargs.get('user_role')
    testsuiteId = kwargs.get('testsuiteId')

    testsuite = Testsuite.get(uid=testsuiteId)

    if not testsuite:
        return http.NotFound('Testsuite is not found')

    if not (user_role == 'admin' or testsuite.public):
        return http.Forbidden()

    return http.Ok(json.dumps(testsuite.to_dict()))

@testsuites_api.route("/testsuites", methods=['POST'])
@auth_required
@group_access_level('admin')
def CreateTestsuite(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    
    name = request.form.get('name')
    level = request.form.get('level')
    public = bool(request.form.get('public'))
    attempts = request.form.get('attempts') or 0
    file = request.files.get('file', None)

    print(attempts)
    timestamp = generate_timestamp()

    if file:
        testcases = parse_testcases_file(file, username, timestamp)
    else:
        testcases = []

    testsuite = Testsuite(
        uid=generate_uuid(),
        name=name,
        level=level,
        public=public,
        attempts=attempts,
        group=groupId,
        testcases=testcases,
        created_at=timestamp,
        created_by=username
    )

    err = testsuite.check()
    if err:
        return http.BadRequest(json.dumps(err))

    testsuite.save()

    data = {'uid':testsuite.uid}
    return http.Created(json.dumps(data))

@testsuites_api.route("/testsuites/<testsuiteId>", methods=['PUT'])
@auth_required
@group_access_level('admin')
def UpdateTestsuite(** kwargs):
    username = kwargs.get('username')
    testsuiteId = kwargs.get('testsuiteId')

    testsuite = Testsuite.get(uid=testsuiteId)
    if not testsuite:
        return http.NotFound('testsuite is not found')

    name = request.json.get('name')
    level = request.json.get('level')
    public = bool(request.json.get('public'))
    attempts = request.json.get('attempts', 0)

    if int(attempts) and int(attempts) < testsuite.attempts:
        return http.BadRequest('new attempts value must be higher than the old value')

    try:
        user = User.get(username=username)
        Testsuite.get(uid=testsuiteId).update(
            name=name, 
            level=level,
            public=public,
            attempts=attempts,
            updated_at=generate_timestamp(),
            updated_by=user
            )
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@testsuites_api.route("/testsuites/<testsuiteId>", methods=['DELETE'])
@auth_required
@group_access_level('admin')
def DeleteTestsuite(** kwargs):
    testsuiteId = kwargs.get('testsuiteId')

    if not Testsuite.get(uid=testsuiteId):
        return http.NotFound('testsuite is not found')

    if Assignment.objects.filter(testsuites=testsuiteId):
        return http.BadRequest("Can't delete testsuite linked to assignment")

    try:
        Testsuite.delete(uid=testsuiteId)
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@testsuites_api.route("/testsuites/<testsuiteId>/testcases/<testcasesId>", methods=['DELETE'])
@auth_required
@group_access_level('admin')
def DeleteTestcase(** kwargs):
    testsuiteId = kwargs.get('testsuiteId')
    testcasesId = kwargs.get('testcasesId')
    testsuite = Testsuite.get(uid=testsuiteId)

    if not testsuite:
        return http.NotFound('testsuite is not found')

    for i, testcase in enumerate(testsuite.testcases):
        if str(testcase.uid) == testcasesId:
            testsuite.testcases.pop(i)
            testsuite.save()
            break
    else:
        return http.NotFound('testcase not found')

    return http.NoContent()

@testsuites_api.route("/testsuites/<testsuiteId>/testcases/suggested", methods=['GET'])
@auth_required
@group_access_level('member')
def ListSuggestTestcases(** kwargs):
    limit = request.args.get('limit', 25, int)
    page = request.args.get('page', 1, int) or 1
    offset = (page - 1) * limit

    user_role = kwargs.get('user_role')
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    testsuiteId = kwargs.get('testsuiteId')

    testsuite = Testsuite.get(uid=testsuiteId)
    if not testsuite:
        return http.NotFound()

    if not (user_role == 'admin' or testsuite.public):
        return http.Forbidden()

    count = SuggestedTestcase.objects(group=groupId, testsuite=testsuiteId).count()
    requested_testcases = SuggestedTestcase.objects(
        group=groupId, 
        testsuite=testsuiteId
    ).order_by('-suggested_at').limit(limit).skip(offset)

    testcases = []
    for testcase in requested_testcases:
        testcases.append(testcase.to_dict())

    pagenation = pagenate(limit, page, count, request.url)

    data = {
        'pagenation': pagenation,
        'result': testcases
    }

    return http.Ok(json.dumps(data))

@testsuites_api.route("/testsuites/<testsuiteId>/testcases", methods=['POST'])
@auth_required
@group_access_level('member')
def AddTestcase(** kwargs):
    user_role = kwargs.get('user_role')
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    testsuiteId = kwargs.get('testsuiteId')
    stdin = request.json.get('stdin')
    expected_stdout = request.json.get('expected_stdout')

    testsuite = Testsuite.get(uid=testsuiteId)

    if not testsuite:
        return http.NotFound('testsuite is not found')

    uid = generate_uuid(5)
    timestamp = generate_timestamp()

    if user_role == 'admin':
        testcase = Testcase(
            uid=uid,
            stdin=stdin,
            expected_stdout=expected_stdout,
            added_by=username,
            added_at=timestamp,
            suggested_by=None
        )

        testsuite.testcases.append(testcase)

        err = testsuite.check()
        if err:
            return http.BadRequest(json.dumps(err))

        testsuite.save()


    elif user_role == 'member':
        
        if not testsuite.public:
            return http.Forbidden()

        testcase = SuggestedTestcase(
            uid=uid,
            user=username,
            group=groupId,
            testsuite=testsuiteId,
            suggested_at=timestamp,
            stdin=stdin,
            expected_stdout=expected_stdout
        )

        err = testcase.check()
        if err:
            return http.BadRequest(json.dumps(err))

        testcase.save()

    data = {'uid':uid}
    return http.Created(json.dumps(data))

@testsuites_api.route("/testsuites/<testsuiteId>/testcases/<testcaseId>/accept", methods=['POST'])
@auth_required
@group_access_level('admin')
def AcceptSuggestedTestcase(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    testsuiteId = kwargs.get('testsuiteId')
    testcaseId = kwargs.get('testcaseId')

    testsuite = Testsuite.get(uid=testsuiteId)
    if not testsuite:
        return http.NotFound('testsuite is not found')

    suggested_testcase = SuggestedTestcase.get(uid=testcaseId)
    if not suggested_testcase:
        return http.NotFound('testcase is not found')

    timestamp = generate_timestamp()

    testcase = Testcase(
        uid=suggested_testcase.uid,
        stdin=suggested_testcase.stdin,
        expected_stdout=suggested_testcase.expected_stdout,
        added_by=username,
        added_at=timestamp,
        suggested_by=suggested_testcase.user.username,        
        suggested_at=suggested_testcase.suggested_at
    )

    testsuite.testcases.append(testcase)
    testsuite.save()

    SuggestedTestcase.delete(uid=testcaseId)

    return http.NoContent()

@testsuites_api.route("/testsuites/<testsuiteId>/testcases/<testcaseId>/reject", methods=['DELETE'])
@auth_required
@group_access_level('member')
def RejectSuggestedTestcase(** kwargs):
    user_role = kwargs.get('user_role')
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    testsuiteId = kwargs.get('testsuiteId')
    testcaseId = kwargs.get('testcaseId')

    testsuite = Testsuite.get(uid=testsuiteId)
    if not testsuite:
        return http.NotFound('testsuite is not found')

    suggested_testcase = SuggestedTestcase.get(uid=testcaseId)
    if not suggested_testcase:
        return http.NotFound('testcase is not found')

    if not (user_role == 'admin' or testsuite.public) and (suggested_testcase.user.username == username):
        return http.Forbidden()
    
    SuggestedTestcase.delete(uid=testcaseId)

    return http.NoContent()


