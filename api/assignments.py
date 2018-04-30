import json, shutil, os, requests, zipfile
from flask import Blueprint, request
from db.models import *
from tools.tools import *
from tools.http import HttpResponse
from werkzeug.utils import secure_filename
from authentication.authenticator import auth_required, group_access_level
from tools.judger import Judger
from pymongo.errors import DocumentTooLarge

http = HttpResponse()
assignments_api = Blueprint('assignments_api', __name__)

config = read_config('config.yaml')

TESTSUITES_ATTACHMENTS = config['dirs']['TESTSUITES_ATTACHMENTS']

@assignments_api.route("/assignments")
@auth_required
@group_access_level('member')
def ListAssignments(** kwargs):
    limit = request.args.get('limit', 25, int)
    page = request.args.get('page', 1, int) or 1
    offset = (page - 1) * limit

    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    
    is_admin = GroupMembership.get(group=groupId, user=username, role='admin')

    if is_admin:
        count = Assignment.objects(group=groupId).count()
        requested_assignments = Assignment.objects(
            group=groupId
        ).order_by('-created_at').limit(limit).skip(offset)
    else:
        count = Assignment.objects(group=groupId, published=True).count()
        requested_assignments = Assignment.objects(
            group=groupId, 
            published=True
        ).order_by('-created_at').limit(limit).skip(offset)
    
    assignments = []
    for assignment in requested_assignments:
        assignments.append(assignment.to_dict())

    pagenation = pagenate(limit, page, count, request.url)

    data = {
        'pagenation': pagenation,
        'result': assignments
    }

    return http.Ok(json.dumps(data))
    
@assignments_api.route("/assignments/<assignmentId>")
@auth_required
@group_access_level('member')
def GetAssignmentInfo(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    assignmentId = kwargs.get('assignmentId')
    
    is_admin = GroupMembership.get(group=groupId, user=username, role='admin')
    assignment = Assignment.get(uid=assignmentId)

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
        uid=generate_uuid(),
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

    data = {'uid':assignment.uid}
    return http.Created(json.dumps(data))

@assignments_api.route("/assignments/<assignmentId>/publish", methods=['POST'])
@auth_required
@group_access_level('admin')
def PublishAssignment(** kwargs):
    username = kwargs.get('username')
    assignmentId = kwargs.get('assignmentId')

    assignment = Assignment.get(uid=assignmentId)
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
        Assignment.objects(uid=assignmentId).update(
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

    assignment = Assignment.get(uid=assignmentId)
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
        Assignment.objects(uid=assignmentId).update(
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

    if not Assignment.get(uid=assignmentId):
        return http.NotFound('Assignment is not found')

    try:
        Assignment.delete(uid=assignmentId)
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@assignments_api.route("/assignments/<assignmentId>/testsuites", methods=['POST'])
@auth_required
@group_access_level('admin')
def linkTestsuite(** kwargs):
    username = kwargs.get('username')
    assignmentId = kwargs.get('assignmentId')

    assignment = Assignment.get(uid=assignmentId)
    if not assignment:
        return http.NotFound('Assignment is not found')

    testsuiteId = request.json.get('testsuiteId')
    testsuite = Testsuite.get(uid=testsuiteId)

    if not testsuite:
        return http.BadRequest("invalid testsuite id")

    if testsuite in assignment.testsuites:
        return http.Conflict('Testsuite already exist')

    try:
        user = User.get(username=username)
        Assignment.objects(uid=assignmentId).update(
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

    assignment = Assignment.get(uid=assignmentId)
    if not assignment:
        return http.NotFound('Assignment is not found')

    if testsuiteId not in [x.uid for x in assignment.testsuites]:
        return http.NotFound('Testsuite is not found')

    if assignment.published and len(assignment.testsuites) < 2:
        return http.BadRequest("Can't delete last testsuite in published assignment")

    try:
        user = User.get(username=username)
        testsuite = Testsuite.get(uid=testsuiteId)
        Assignment.objects(uid=assignmentId).update_one(
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
    source_file = request.files.get('source_file')

    group = Group.get(uid=groupId)
    assignment = Assignment.get(uid=assignmentId)
    testsuite = Testsuite.get(uid=testsuiteId)

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

    if not source_file:
        return http.BadRequest('no selected file')

    reference_id = generate_uuid(20)

    user_temp_dir = '{0}/{1}'.format(
        config['dirs']['USERS_TMP_CODE_DIR'],
        reference_id
    )

    os.mkdir(user_temp_dir)

    source_file_path =  '{0}/{1}/{2}'.format(
        config['dirs']['USERS_TMP_CODE_DIR'],
        reference_id,
        source_file.filename
    )
    source_file.save(source_file_path)

    if testsuite.attachment:
        for attachment in testsuite.attachment:
            attachment_uid = '%s_%s' % (testsuite.uid, attachment)
            attachment_path = os.path.join(TESTSUITES_ATTACHMENTS, attachment_uid)
            shutil.copyfile(attachment_path, os.path.join(user_temp_dir, attachment))
            
    ext = source_file.filename[source_file.filename.rfind('.')+1:]

    if ext not in ['zip', 'cpp']:
        shutil.rmtree(user_temp_dir)
        return http.BadRequest('Unsupported file format (.%s), supports only (.zip & .cpp)' % (ext))

    if ext in 'zip':
        try:
            file = zipfile.ZipFile(source_file_path)
            file.extractall(path=user_temp_dir)
            file.close()
        except:
            shutil.rmtree(user_temp_dir)
            return http.BadRequest('Cannot uncommpress your file, file maybe is corrupted')

    try:
        judger = Judger(reference_id=reference_id)
        judger_result = judger.judge(testsuite.to_dict()['testcases'])
    except:
        return http.InternalServerError('Unexpected error')
    finally:
        shutil.rmtree(user_temp_dir)
    
    status = 'unknown'
    compiler_result = judger_result['compiler']
    if compiler_result:
        if compiler_result['returncode']:
            status = 'Compiler Error'
        else:
            test_summary = judger_result['summary']
            if test_summary['errored']:
                status = 'Error'
            elif test_summary['failed']:
                status = 'Failed'
            else:
                status = 'Passed'

    submission = Submission(
        uid=reference_id,
        group=groupId,
        assignment=assignmentId,
        testsuite=testsuiteId,
        submitted_at=generate_timestamp(),
        username=username,
        language=language,
        result=judger_result,
        status=status
    )
    err = submission.check()
    if err:
        return http.InternalServerError(json.dumps(err))

    try:
        submission.save()
    except DocumentTooLarge:
        return "Can't return your result because it is too large, please make sure your code doesn't print huge amount of data in stdout", 422
    except:
        return http.InternalServerError()

    return http.Created(json.dumps({'uid':reference_id}))

@assignments_api.route("/assignments/<assignmentId>/submissions")
@auth_required
@group_access_level("member")
def ListSubmissions(**kwargs):
    limit = request.args.get('limit', 25, int)
    page = request.args.get('page', 1, int) or 1
    offset = (page - 1) * limit

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

    count = Submission.objects(group=groupId, assignment=assignmentId, **query).count()
    submissions = Submission.objects(
        group=groupId, 
        assignment=assignmentId,
        **query).order_by('-submitted_at').limit(limit).skip(offset)

    pagenation = pagenate(limit, page, count, request.url)

    data = {
        'pagenation': pagenation,
        'result': json.loads(submissions.to_json())
    }
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
                    '$sum':{
                        '$cond':[{'$ne': ['$status', 'Passed']}, 1, 0]
                    }
                },
                'status':{
                    '$push':'$status'
                },
                'score':{
                    '$max':{
                        '$cond':[{'$eq': ['$status', 'Passed']}, '$result.summary.passed', 0] 
                    }
                },
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
                        'score':'$score'
                    }
                },
                'total_score':{
                    '$sum':'$score'
                },
                'total_wrong_try':{
                    '$sum':'$attempts'
                }
            }
        },
         {
            '$sort': {
                'total_score' : -1,
                 'total_wrong_try': 1
                } 
            }
    ]

    result = Submission.objects.aggregate(*pipeline)
    return json.dumps(list(result))