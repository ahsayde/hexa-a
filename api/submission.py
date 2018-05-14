import json, os
from flask import Blueprint
from tools.http import HttpResponse
from db.models import Submission, GroupMembership
from authentication.authenticator import auth_required

http = HttpResponse()
submission_api = Blueprint('submission_api', __name__)

@submission_api.route("/submissions/<submissionId>")
@auth_required
def getSubmission(**kwargs):
    username = kwargs.get('username')
    submissionId = kwargs.get('submissionId')

    submission = Submission.get(uid=submissionId)
    if not submission:
        return http.NotFound()

    groupId = submission.group.uid
    group_membership = GroupMembership.get(group=groupId, user=username)

    if not group_membership:
        return http.Forbidden()
    
    result = submission.to_dict()

    if group_membership.role != 'admin':
        if submission.username != username:        
            return http.Forbidden()
        
        if not submission.testsuite.public:
            del result['result']['testcases']

    return http.Ok(json.dumps(result))
