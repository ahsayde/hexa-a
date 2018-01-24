import json
from db.models import *
from tools.tools import *
from flask import Blueprint, request
from tools.http import HttpResponse
from authentication.authenticator import auth_required, group_access_level

http = HttpResponse()
groups_api = Blueprint('groups_api', __name__)

@groups_api.route("/groups")
@auth_required
def ListGroups(** kwargs):
    username = kwargs.get('username')
    groups = []
    memberships = GroupMembership.objects(user=username)
    for membership in memberships:
        group = membership.group.to_dict()
        group['is_admin'] = bool(membership.role == 'admin')
        group['is_member'] = bool(membership.role == 'member')
        group['members_count'] = GroupMembership.objects(group=group['_id']).count()

        join_request =  GroupJoinRequest.get(user=username, group=group['_id'])
        if join_request:
            group['join_request'] = join_request._id
        else:
            group['join_request'] = None

        groups.append(group)

    return http.Ok(json.dumps(groups))

@groups_api.route("/groups/<groupId>")
@auth_required
def GetGroupInfo(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    
    group = Group.get(_id=groupId)
    if not group:
        return http.NotFound('Group not found')

    membership = GroupMembership.get(group=groupId, user=username)
    group = group.to_dict()
    if membership:
        group['is_admin'] = bool(membership.role == 'admin')
        group['is_member'] = bool(membership.role == 'member')
    else:
        group['is_admin'] = False
        group['is_member'] = False

    join_request =  GroupJoinRequest.get(user=username, group=group['_id'])
    if join_request:
        group['join_request'] = join_request._id
    else:
        group['join_request'] = None

    group['members_count'] = GroupMembership.objects(group=groupId).count()
    group['join_requests_count'] = GroupJoinRequest.objects(group=groupId).count()
        
    return http.Ok(json.dumps(group))

@groups_api.route("/groups", methods=['POST'])
@auth_required
def CreateGroup(**kwargs):
    username = kwargs.get('username')
    _id = generate_uuid()
    name = request.json.get('name', '')
    description = request.json.get('description', '')

    timestamp = generate_timestamp()

    group = Group(
        _id=_id,
        name=name,
        description=description,
        created_at=timestamp,        
        created_by=username,
        updated_at=timestamp,
        updated_by=username
    )

    err = group.check()
    if err:
        return http.BadRequest(json.dumps(err))

    _id = generate_uuid()
    joined_at = generate_timestamp()
    membership = GroupMembership(
        _id=_id,
        group=group,
        user=username,
        role='admin',
        joined_at=joined_at,
        added_by=username
    )

    err = membership.check()
    if err:
        return http.InternalServerError(
            'Error when store membership data'
    )

    group.save()
    membership.save()

    return http.Created(json.dumps({'_id':group._id}))

@groups_api.route("/groups/<groupId>", methods=['PUT'])
@auth_required
@group_access_level('admin')
def UpdateGroup(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    
    name = request.json.get('name', '')
    description = request.json.get('description', '')

    try:
        user = User.get(username=username)
        Group.get(_id=groupId).update(
            name=name,
            description=description,
            updated_at=generate_timestamp(),
            updated_by=user
        )
    except Exception as e:
        return http.InternalServerError(json.dumps(e.args))

    return http.NoContent()

@groups_api.route("/groups/<groupId>", methods=['DELETE'])
@auth_required
@group_access_level('admin')
def DeleteGroup(**kwargs):    
    groupId = kwargs.get('groupId')
    try:
        Group.delete(_id=groupId)
    except Exception as e:
        return http.InternalServerError(e.args)

    return http.NoContent()

@groups_api.route("/groups/<groupId>/members")
@auth_required
@group_access_level('members')
def ListGroupMembership(**kwargs):
    groupId = kwargs.get('groupId')
    fields = ['user', 'joined_at', 'added_by', 'role']
    members = GroupMembership.objects(group=groupId).only(*fields)
    data = []
    for member in members:
        data.append(member.to_dict())

    return http.Ok(json.dumps(data))

@groups_api.route("/groups/<groupId>/members", methods=['POST'])
@auth_required
@group_access_level('admin')
def addUserToGroup(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    member = request.json.get('member')
    role = request.json.get('role', 'member')

    if not User.get(username=member):
        return http.BadRequest('User not exists')

    if role not in ['admin', 'member']:
        return http.BadRequest('Invalid role')

    if GroupMembership.objects(group=groupId, user=member):
        return http.Conflict('User is already a member group')

    _id = generate_uuid()
    joined_at = generate_timestamp()
    membership = GroupMembership(
        _id=_id,
        group=groupId,
        user=member,
        role=role,
        joined_at=joined_at,
        added_by=username
    )

    err = membership.check()
    if err:
        return http.InternalServerError(
            'Error when store membership data'
    )

    membership.save()
    GroupJoinRequest.delete(user=member, group=groupId)

    return http.Created()

@groups_api.route("/groups/<groupId>/members/<member>", methods=['PUT'])
@auth_required
@group_access_level('admin')
def updateUserGroupMembership(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    member = kwargs.get('member')
    
    membership = GroupMembership.get(group=groupId, user=member)
    if not membership:
        return http.NotFound('User is not a member in group')

    role = request.json.get('role', None)

    if role == 'member' and membership.role == 'admin':
        if GroupMembership.objects(group=groupId, role='admin').count() < 2:
            return http.BadRequest("Can't change the role of the last admin in group to member")

    try:
        GroupMembership.objects(group=groupId, user=member).update(role=role)
    except Exception as e:
        return http.InternalServerError(e.args)

    return http.NoContent()

@groups_api.route("/groups/<groupId>/members/<member>", methods=['DELETE'])
@auth_required
@group_access_level('mebmer')
def removeUserFromGroup(**kwargs):
    user_role = kwargs.get('user_role')
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    member = kwargs.get('member')

    if not (user_role == 'admin' or username == member):
        return http.Forbidden()

    membership = GroupMembership.get(group=groupId, user=member)
    if not membership:
        return http.NotFound('User is not a member in group')

    if membership.role == 'admin' and GroupMembership.objects(group=groupId, role='admin').count() < 2:
        return http.BadRequest("Can't remove the last admin in group")

    try:
        GroupMembership.delete(group=groupId, user=member)
    except Exception as e:
        return http.InternalServerError(e.args)

    return http.NoContent()

@groups_api.route("/groups/<groupId>/requests")
@auth_required
@group_access_level('admin')
def ListJoinRequests(**kwargs):
    groupId = kwargs.get('groupId')
    requests = GroupJoinRequest.objects(group=groupId)

    data = []
    for request in requests:
        data.append(request.to_dict())
    
    return http.Ok(json.dumps(data))

@groups_api.route("/groups/<groupId>/requests/<requestId>", methods=['POST'])
@auth_required
@group_access_level('admin')
def AcceptJoinRequest(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    requestId = kwargs.get('requestId')

    join_request = GroupJoinRequest.get(_id=requestId, group=groupId)
    if not join_request:
        return http.NotFound()

    _id = generate_uuid()
    timestamp = generate_timestamp()

    new_membership = GroupMembership(
        _id=_id,
        group=join_request.group,
        user=join_request.user,
        role='member',
        joined_at=timestamp,
        added_by=username
    )

    err = new_membership.check()
    if err:
        return http.InternalServerError('Error when store membership data')

    new_membership.save()
    GroupJoinRequest.delete(_id=requestId)

    return http.NoContent()

@groups_api.route("/groups/<groupId>/requests/<requestId>", methods=['DELETE'])
@auth_required
@group_access_level('admin')
def RejectJoinRequest(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    requestId = kwargs.get('requestId')

    join_request = GroupJoinRequest.get(_id=requestId, group=groupId)
    if not join_request:
        return http.NotFound()

    GroupJoinRequest.delete(_id=requestId)

    return http.NoContent()


@groups_api.route("/groups/<groupId>/join", methods=['POST'])
@auth_required
def SendJoinRequest(**kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')

    group = Group.get(_id=groupId)
    if not group:
        return http.NotFound('Group not found')

    membership = GroupMembership.get(group=groupId, user=username)
    if membership:
        return http.Conflict('User is already member in the group')

    if GroupJoinRequest.get(group=groupId, user=username):
        return http.Conflict('Join request already send')

    _id = generate_uuid()
    timestamp = generate_timestamp()

    join_request = GroupJoinRequest(
        _id=_id,
        user=username,
        group=groupId,
        created_at=timestamp
    )

    err = join_request.check()
    if err:
        return http.InternalServerError('Error when store join request data')

    join_request.save()

    data = {'_id':_id}
    return http.Created(json.dumps(data))