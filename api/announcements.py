import json
from flask import Blueprint, request
from db.models import *
from tools.tools import *
from tools.http import HttpResponse
from authentication.authenticator import auth_required, group_access_level

http = HttpResponse()
announcements_api = Blueprint('announcements_api', __name__)

@announcements_api.route("/announcements")
@auth_required
@group_access_level('member')
def ListAnnouncements(** kwargs):
    limit = request.args.get('limit', 25, int)
    page = request.args.get('page', 1, int) or 1
    offset = (page - 1) * limit

    groupId = kwargs.get('groupId')
    count = Announcement.objects(group=groupId).count()
    requested_announcements = Announcement.objects(group=groupId).order_by('-created_at').limit(limit).skip(offset)

    announcements = []
    for announcement in requested_announcements:
        announcements.append(announcement.to_dict())

    pagenation = pagenate(limit, page, count, request.url)

    data = {
        'pagenation': pagenation,
        'result': announcements
    }

    return http.Ok(json.dumps(data))

@announcements_api.route("/announcements", methods=['POST'])
@auth_required
@group_access_level('admin')
def CreateAnnouncement(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    content = request.json.get('content')

    announcement = Announcement(
        uid=generate_uuid(),
        content=content,
        group=groupId,
        created_at=generate_timestamp(),
        created_by=username
    )

    err = announcement.check()
    if err:
        return http.BadRequest(json.dumps(err))

    announcement.save()

    data = {'uid':announcement.uid}
    return http.Created(json.dumps(data))

@announcements_api.route("/announcements/<announcementId>", methods=['PUT'])
@auth_required
@group_access_level('admin')
def UpdateAnnouncement(** kwargs):
    username = kwargs.get('username')
    announcementId = kwargs.get('announcementId')

    announcement = Announcement.get(uid=announcementId)

    if not announcement:
        return http.NotFound('Announcement is not found')

    if announcement.created_by.username != username:
        return http.Forbidden()

    content = request.json.get('content')
            
    try:
        Announcement.get(uid=announcementId).update(
            content=content,
            updated_at=generate_timestamp()
        )
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@announcements_api.route("/announcements/<announcementId>", methods=['DELETE'])
@auth_required
@group_access_level('admin')
def DeleteAnnouncement(** kwargs):
    announcementId = kwargs.get('announcementId')

    if not Announcement.get(uid=announcementId):
        return http.NotFound('Announcement is not found')

    try:
        Announcement.delete(uid=announcementId)
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()