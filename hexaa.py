import os
from flask import Flask
from db.db import Database
from tools.tools import read_config
from api import *
from views import *
from authentication.auth_service import auth_service
from minio import Minio

class HEXAA:
    def __init__(self):
        self._config = read_config()
        self._app = Flask(__name__, template_folder='templates', static_folder='static')
        # load config
        self._load_config()
        # set session secret
        self._app.secret_key = os.environ.get("SESSION_SECRET")
        # connect to database
        self._connect_to_database(self._config['database'])
        # load api blueprints
        self._load_api_blueprints()
        # load portal bluprint
        self._load_portal_blueprints()
        # create required buckets
        self._make_storage_buckets()

    def _load_config(self):
        self._app.config.update(self._config)

    def _connect_to_database(self, config):
        self._db = Database()
        self._db.connect(** config)

    def _make_storage_buckets(self):
        minio_url = self._config["minio"]["url"] or "localhost:9000"
        minio_key = os.environ.get("MINIO_ACCESS_KEY", self._config["minio"]["key"])
        minio_secret = os.environ.get("MINIO_SECRET_KEY", self._config["minio"]["secret"])
        # import ipdb; ipdb.set_trace()
        miniocl = Minio(minio_url, minio_key, minio_secret, secure=False)
        self._app.config["miniocl"] = miniocl
        for bucket in ["pictures", "submissions", "testsuites"]:
            if not miniocl.bucket_exists(bucket):
                miniocl.make_bucket(bucket)

    def _load_api_blueprints(self):
        self._app.register_blueprint(auth_service)
        self._app.register_blueprint(users_api, url_prefix='/api')
        self._app.register_blueprint(groups_api, url_prefix='/api')
        self._app.register_blueprint(submission_api, url_prefix='/api')        
        self._app.register_blueprint(assignments_api, url_prefix='/api/groups/<groupId>')
        self._app.register_blueprint(announcements_api, url_prefix='/api/groups/<groupId>')
        self._app.register_blueprint(testsuites_api, url_prefix='/api/groups/<groupId>')

    def _load_portal_blueprints(self):
        self._app.register_blueprint(main_pages)
        self._app.register_blueprint(user_pages)        
        self._app.register_blueprint(group_pages)
        self._app.register_blueprint(assignments_pages)
        self._app.register_blueprint(announcements_pages)   
        self._app.register_blueprint(testsuites_pages)
        self._app.register_blueprint(submissions_pages) 
        self._app.register_blueprint(members_page) 
        self._app.register_blueprint(settings_page)
