# from functools import wraps
# from flask import request
# from tools.tools import generate_timestamp, generate_uuid
# from db.models import *

# class Notifications(object):
#     def __init__(self, func, event):
#         self.func = func
#         self.event = event
#         wraps(func)(self)

#     def __call__(self, *args, **kwargs):
#         response = self.func(*args, **kwargs)
#         if response._status_code < 399:
#             self.newJoinRequest(**kwargs)
#         return response

#     def newJoinRequest(self, **kwargs):
#         group = Group.get(_id=kwargs.get('groupId'))
#         notification = Notification(
#             _id=generate_uuid(),
#             event_type='NewJoinRequest',
#             created_at=generate_timestamp(),
#             entity=group._id,
#             data={
#                 'group':group.to_dict(),
#                 'from_user':kwargs.get('username')
#             }
#         )
#         notification.save()

# def notify(entity_type):
#     def _notify(func):
#         return Notifications(func, entity_type)
#     return _notify