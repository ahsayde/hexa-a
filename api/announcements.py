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
    groupId = kwargs.get('groupId')
    announcements = Announcement.objects(group=groupId).order_by('-created_at')
    data = []
    for announcement in announcements:
        data.append(announcement.to_dict())
    return http.Ok(json.dumps(data))
    
@announcements_api.route("/announcements", methods=['POST'])
@auth_required
@group_access_level('admin')
def CreateAnnouncement(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    content = request.json.get('content')

    announcement = Announcement(
        _id=generate_uuid(),
        content=content,
        group=groupId,
        created_at=generate_timestamp(),
        created_by=username
    )

    err = announcement.check()
    if err:
        return http.BadRequest(json.dumps(err))

    announcement.save()

    data = {'_id':announcement._id}
    return http.Created(json.dumps(data))


@announcements_api.route("/announcements/<announcementId>", methods=['PUT'])
@auth_required
@group_access_level('admin')
def UpdateAnnouncement(** kwargs):
    username = kwargs.get('username')
    announcementId = kwargs.get('announcementId')

    announcement = Announcement.get(_id=announcementId)

    if not announcement:
        return http.NotFound('Announcement is not found')

    if announcement.created_by.username != username:
        return http.Forbidden()

    content = request.json.get('content')
            
    try:
        Announcement.get(_id=announcementId).update(
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

    if not Announcement.get(_id=announcementId):
        return http.NotFound('Announcement is not found')

    try:
        Announcement.delete(_id=announcementId)
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()