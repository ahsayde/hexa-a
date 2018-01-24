import mongoengine

class Database:
    def __init__(self):
        pass

    def connect(self, db, host, port, username=None, password=None):
        mongoengine.connect(
            db=db,
            host=host,
            port=port,
            username=username,
            password=password
        )
