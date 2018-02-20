import requests
from flask import session
from client.groups import Groups
from client.users import Users
from client.authentication import Authentication

class Client:
    
    def __init__(self, url='http://localhost'):
        self.base_url = url
        self.api_url = self.base_url + '/api'
        self.session = requests.session()
        self.groups = Groups(self)
        self.users = Users(self)
        self.authentication = Authentication(self)

    def set_auth_header(self, value):
        self.session.headers['AUTH-TOKEN'] = value

    def api_handler(self, url, method, content_type='application/json', params=None, data=None, headers=None):
        
        self.session.headers['Content-Type'] = content_type

        if method == 'get':
            response =  self.get(url=url, params=params, headers=headers)
        elif method == 'post':
            response = self.post(url=url, params=params, data=data, headers=headers)
        elif method == 'put':
            response = self.put(url=url, params=params, data=data, headers=headers)
        elif method == 'delete':
            response = self.delete(url=url, params=params, headers=headers)

        response.raise_for_status()
        return response
                

    def get(self, url, params=None, headers=None):
        return self.session.get(url=url, params=params, headers=headers)

    def post(self, url, params=None, data=None, headers=None):
        return self.session.post(url=url, params=params, json=data, headers=headers)

    def put(self, url, params=None, data=None, headers=None):
        return self.session.put(url=url, params=params, json=data, headers=headers)
  
    def delete(self, url, params=None, headers=None):
        return self.session.delete(url=url, params=params, headers=headers)
