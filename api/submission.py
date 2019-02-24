import json, os
from flask import Blueprint
from tools.tools import read_config
from tools.http import HttpResponse
from db.models import Submission, GroupMembership
from authentication.authenticator import auth_required
from urllib import parse
from minio import Minio

http = HttpResponse()
submission_api = Blueprint('submission_api', __name__)

config = read_config('config.yaml')

minioconf = config["minio"]
minio_key = os.environ.get("MINIO_ACCESS_KEY") or minioconf["key"]
minio_secret = os.environ.get("MINIO_SECRET_KEY") or  minioconf["secret"]
miniocl = Minio(minioconf["url"], minio_key, minio_secret, secure=False)

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
            del result['result']

    return http.Ok(json.dumps(result))

@submission_api.route("/submissions/<submissionId>/download")
@auth_required
def DownlodFile(**kwargs):
    username = kwargs.get('username')
    submissionId = kwargs.get('submissionId')

    submission = Submission.get(uid=submissionId)
    if not submission:
        return http.NotFound()

    groupId = submission.group.uid
    group_membership = GroupMembership.get(group=groupId, user=username)

    if not submission.file_ref:
        return http.BadRequest()

    if not group_membership:
        return http.Forbidden()
    
    if group_membership.role != 'admin':
        if submission.username != username:
            return http.Forbidden()

    object_url = miniocl.presigned_get_object('submissions', submission.file_ref)
    url_obj = parse.urlparse(object_url)
    url = "/files" +  url_obj.path + "?" + url_obj.query
    return json.dumps({"url": url})
    