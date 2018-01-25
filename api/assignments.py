import json, shutil, os
from flask import Blueprint, request
from db.models import *
from tools.tools import *
from tools.http import HttpResponse
from tools.checker import Judger
from werkzeug.utils import secure_filename
from authentication.authenticator import auth_required, group_access_level

http = HttpResponse()
assignments_api = Blueprint('assignments_api', __name__)

USERS_TMP_CODE_DIR = read_config()['dirs']['USERS_TMP_CODE_DIR']

@assignments_api.route("/assignments")
@auth_required
@group_access_level('member')
def ListAssignments(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    
    is_admin = GroupMembership.get(group=groupId, user=username, role='admin')

    if is_admin:
        assignments = Assignment.objects(group=groupId)
    else:
        assignments = Assignment.objects(group=groupId, published=True)
        
    return http.Ok(assignments.to_json())
    
@assignments_api.route("/assignments/<assignmentId>")
@auth_required
@group_access_level('member')
def GetAssignmentInfo(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    assignmentId = kwargs.get('assignmentId')
    
    is_admin = GroupMembership.get(group=groupId, user=username, role='admin')
    assignment = Assignment.get(_id=assignmentId)

    if not is_admin and not assignment.published:
        return http.Forbidden()

    if not assignment:
        return http.NotFound('Assignment is not found')

    data = assignment.to_dict()

    if assignment.deadline:
        if assignment.deadline >= int(time.time()):
            data['status'] = 'open'
        else:
            data['status'] = 'closed'
    else:
        data['status'] = 'open'
           
    return http.Ok(json.dumps(data))

@assignments_api.route("/assignments", methods=['POST'])
@auth_required
@group_access_level('admin')
def CreateAssignment(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    name = request.json.get('name')
    description = request.json.get('description', '')
    deadline = datetimeToEpoc(request.json.get('deadline', None))

    if deadline:
        if deadline <= int(time.time()):
            return http.BadRequest("Deadline must be after current time")

    assignment = Assignment(
        _id=generate_uuid(),
        name=name,
        description=description,
        deadline=deadline,
        group=groupId,
        created_at=generate_timestamp(),
        created_by=username
    )

    err = assignment.check()
    if err:
        return http.BadRequest(json.dumps(err))

    assignment.save()

    data = {'_id':assignment._id}
    return http.Created(json.dumps(data))

@assignments_api.route("/assignments/<assignmentId>/publish", methods=['POST'])
@auth_required
@group_access_level('admin')
def PublishAssignment(** kwargs):
    username = kwargs.get('username')
    assignmentId = kwargs.get('assignmentId')

    assignment = Assignment.get(_id=assignmentId)
    if not assignment:
        return http.NotFound('Assignment is not found')
    
    if assignment.published:
        return http.Conflict('Assignment is already published')

    if not assignment.testsuites:
        return http.BadRequest("Can't publish assignment without at least on testsuite")

    if assignment.deadline:
        if assignment.deadline <= int(time.time()):
            return http.BadRequest('Can\'t publish assignment with old deadline')
        
    try:
        user = User.get(username=username)
        Assignment.objects(_id=assignmentId).update(
            published=True,
            published_at=generate_timestamp(),
            published_by=user
        )
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@assignments_api.route("/assignments/<assignmentId>", methods=['PUT'])
@auth_required
@group_access_level('admin')
def UpdateAssignment(** kwargs):
    username = kwargs.get('username')
    assignmentId = kwargs.get('assignmentId')

    assignment = Assignment.get(_id=assignmentId)
    if not assignment:
        return http.NotFound('Assignment is not found')

    name = request.json.get('name')
    description = request.json.get('description', '')
    settings = request.json.get('settings', None)
    deadline = datetimeToEpoc(request.json.get('deadline', None))

    if deadline:
        if assignment.published:
            if deadline <= assignment.published_at:
                return http.BadRequest("Deadline must be after publication time")

        if deadline <= int(time.time()):
            return http.BadRequest("Deadline must be after current time")
            
    try:
        user = User.get(username=username)
        Assignment.objects(_id=assignmentId).update(
            name=name, 
            description=description,
            settings=settings,
            deadline=deadline,
            updated_at=generate_timestamp(),
            updated_by=user
        )
    except Exception as e:
        print(e.args)
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@assignments_api.route("/assignments/<assignmentId>", methods=['DELETE'])
@auth_required
@group_access_level('admin')
def DeleteAssignment(** kwargs):
    
    assignmentId = kwargs.get('assignmentId')

    if not Assignment.get(_id=assignmentId):
        return http.NotFound('Assignment is not found')

    try:
        Assignment.delete(_id=assignmentId)
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@assignments_api.route("/assignments/<assignmentId>/testsuites", methods=['POST'])
@auth_required
@group_access_level('admin')
def linkTestsuite(** kwargs):
    username = kwargs.get('username')
    assignmentId = kwargs.get('assignmentId')

    assignment = Assignment.get(_id=assignmentId)
    if not assignment:
        return http.NotFound('Assignment is not found')

    testsuiteId = request.json.get('testsuiteId')
    testsuite = Testsuite.get(_id=testsuiteId)

    if not testsuite:
        return http.BadRequest("invalid testsuite id")

    if testsuite in assignment.testsuites:
        return http.Conflict('Testsuite already exist')

    try:
        user = User.get(username=username)
        Assignment.objects(_id=assignmentId).update(
            push__testsuites=testsuite,
            updated_at=generate_timestamp(),
            updated_by=user
        )
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.Created()

@assignments_api.route("/assignments/<assignmentId>/testsuites/<testsuiteId>", methods=['DELETE'])
@auth_required
@group_access_level('admin')
def unlinkTestsuite(** kwargs):
    username = kwargs.get('username')
    assignmentId = kwargs.get('assignmentId')
    testsuiteId = kwargs.get('testsuiteId')

    assignment = Assignment.get(_id=assignmentId)
    if not assignment:
        return http.NotFound('Assignment is not found')

    if testsuiteId not in [x._id for x in assignment.testsuites]:
        return http.NotFound('Testsuite is not found')

    if assignment.published and len(assignment.testsuites) < 2:
        return http.BadRequest("Can't delete last testsuite in published assignment")

    try:
        user = User.get(username=username)
        testsuite = Testsuite.get(_id=testsuiteId)
        Assignment.objects(_id=assignmentId).update_one(
            pull__testsuites=testsuite,
            updated_at=generate_timestamp(),
            updated_by=user
        )
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@assignments_api.route("/assignments/<assignmentId>/submit", methods=['POST'])
@auth_required
@group_access_level("member")
def submit(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    assignmentId = kwargs.get('assignmentId')
    testsuiteId = request.form.get('testsuite')
    language = request.form.get('language')
    file = request.files.get('source_file')

    group = Group.get(_id=groupId)
    assignment = Assignment.get(_id=assignmentId)
    testsuite = Testsuite.get(_id=testsuiteId)

    if testsuite.attempts > 0:
        user_submissions =  Submission.objects(
            username=username,
            assignment=assignmentId,
            testsuite=testsuiteId,    
        ).count()

        if user_submissions >= testsuite.attempts:
            return http.Forbidden()

    if not assignment:
        return http.BadRequest('invalid assignment id')

    if not testsuite:
        return http.BadRequest('invalid testsuite id')

    if assignment.deadline:
        if assignment.deadline <= int(time.time()):
            return http.Forbidden('Can\'t submit to closed assignment')

    config = read_config('judger_config.yaml')

    if language not in config['languages'].keys():
        return http.BadRequest('Unsupported language')

    if not file:
        return http.BadRequest('no selected file')

    reference_id = generate_uuid(20)
    tmp_directory = USERS_TMP_CODE_DIR + reference_id

    os.mkdir(tmp_directory)
    source_file = secure_filename(file.filename)
    file.save(os.path.join(tmp_directory, source_file))
    language_config = config['languages'][language]
    judger = Judger(language_config)

    try:
        judger.judge(tmp_directory, source_file, testsuite)
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    status = 'unknown'
    compiler_result = judger.result['compiler']
    if compiler_result:
        if compiler_result['returncode']:
            status = 'Compiler Error'
        else:
            test_summary = judger.result['summary']
            if test_summary['errored']:
                status = 'Error'
            elif test_summary['failed']:
                status = 'Failed'
            else:
                status = 'Passed'

    submission = Submission(
        _id=reference_id,
        group=groupId,
        assignment=assignmentId,
        testsuite=testsuiteId,
        submitted_at=generate_timestamp(),
        username=username,
        language=language,
        result=judger.result,
        status=status
    )
    err = submission.check()
    if err:
        return http.InternalServerError(json.dumps(err))

    submission.save()

    return http.Created(json.dumps({'_id':reference_id}))

@assignments_api.route("/assignments/<assignmentId>/submissions")
@auth_required
@group_access_level("member")
def ListSubmissions(**kwargs):
    user_role = kwargs.get('user_role')
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    assignmentId = kwargs.get('assignmentId')

    query = {}
    data = []
    admin_filters = ['username', 'testsuite', 'status']
    member_filters = ['testsuite', 'status']

    if user_role == 'admin':
        for filter in admin_filters:
            value = request.args.get(filter)
            if value:
                query[filter] = value
    
    elif user_role == 'member':
        query['username'] = username
        for filter in member_filters:
            value = request.args.get(filter)
            if value:
                query[filter] = value

    submissions = Submission.objects(group=groupId, assignment=assignmentId, **query)
    
    for submission in submissions:
        temp = submission.to_dict()
        temp['summary'] = temp['result']['summary']
        del temp['result']
        data.append(temp)

    return http.Ok(json.dumps(data))

@assignments_api.route("/assignments/<assignmentId>/leaderboard")
@auth_required
@group_access_level("member")
def Board(**kwargs):
    groupId = kwargs.get('groupId')
    assignmentId = kwargs.get('assignmentId')

    pipeline = [
        {
            '$match': {
                'group':groupId,
                'assignment':assignmentId
            }
        },
        {
            '$group':{
                '_id':{
                    'username':'$username',
                    'testsuite':'$testsuite'
                },
                'attempts':{
                    '$sum': 1
                },
                'status':{
                    '$push':'$status'
                }
            }
        },
        {
            '$group':{
                '_id':'$_id.username',
                'testsuites':{
                    '$push':{
                        'status':'$status',
                        'attempts':'$attempts',
                        'testsuite':'$_id.testsuite',
                        'summary':'$summary'
                    }
                },
            }
        },
        # {
        #     '$group': {
        #         '_id': {
        #             'username':'$username',
        #             'testsuite': "$testsuite",
        #         },
        #         'attempts':{
        #             '$sum': 1
        #         },
        #         'submissions':{
        #             '$push':{
        #                 '_id':'$_id',
        #                 'status':'$status'
        #             }
        #         }
        #     }
        # }, 
        # {
        #     '$group': {
        #         '_id': "$_id.username", 
        #         'testsuites':{
        #             '$push': {
        #                 'attempts': "$attempts", 
        #                 'testsuite':'$_id.testsuite', 
        #                 'submissions': "$submissions"
        #             }
        #         }
        #     }
        #}
    ]

    result = Submission.objects.aggregate(*pipeline)
    return json.dumps(list(result))




















