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

    if submission.username != username:
        groupId = submission.group.uid
        group_membership = GroupMembership.get(group=groupId, user=username)
        if not group_membership:
            return http.Forbidden()

        if group_membership.role != 'admin':
            return http.Forbidden()

    return http.Ok(json.dumps(submission.to_dict()))
