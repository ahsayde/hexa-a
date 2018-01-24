import time
from tools.tools import *
from db.models import User, Session
from flask import session as client_session

class SessionManager:

    def __init__(self):
        pass
    
    def create_session(self, user_id, jwt, timestamp):
        session = Session(
            key=generate_uuid(),
            user_id=user_id,
            jwt=jwt,
            created_at=timestamp,
            expires_at=(timestamp + 8600),
        )

        client_session['key'] = session.key
        client_session['user_id'] = session.user_id
        client_session['created_at'] = session.created_at
        client_session['expires_at'] = session.expires_at
        client_session['jwt'] = session.jwt

        session.save()

        
    def destroy_session(self, key):
        Session.delete(key=key)
        client_session.clear()

    def get_current_session(self):
        return client_session

    def is_valid_session(self, key):
        session = Session.get(key=key)
        if not session:
            return False
        
        if session.expires_at < time.time():
            self.destroy_session(key=key)
            return False
        
        return True



    

    
        
