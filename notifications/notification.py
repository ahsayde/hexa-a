from functools import wraps
from flask import request
from tools.tools import generate_timestamp, generate_uuid
from db.models import Notification, Testsuite, Group, User

class Notifications(object):
    def __init__(self, func, event):
        self.func = func
        self.event = event
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        response = self.func(*args, **kwargs)
        if response._status_code < 399:
            self.pushNotification(** kwargs)
        return response

    def pushNotification(self, **kwargs):
        pass
    
def notify(entity_type):
    def _notify(func):
        return Notifications(func, entity_type)
    return _notify