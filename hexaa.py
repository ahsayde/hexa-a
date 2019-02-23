from flask import Flask
from db.db import Database
from tools.tools import read_config
from api import *
from views import *
from authentication.auth_service import auth_service
# from views.group import group_page

class HEXAA:
    def __init__(self):
        self._config = read_config()
        self._app = Flask(__name__, template_folder='templates', static_folder='static')
        # set session secret
        self._app.secret_key = os.environ.get("SESSION_SECRET")
        # connect to database
        self._connect_to_database(self._config['database'])
        # load api blueprints
        self._load_api_blueprints()
        # load portal bluprint
        self._load_portal_blueprints()

    def _connect_to_database(self, config):
        self._db = Database()
        self._db.connect(** config)

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