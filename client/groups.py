from client.assignments import Assignments
from client.testsuites import Testsuites
from client.member import Members
from client.submissions import Submissions
from client.request import Requests

class Groups:
    def __init__(self, client):
        self.client = client
        self.members = Members(client)
        self.assignments = Assignments(client)
        self.testsuites = Testsuites(client)
        self.submissions = Submissions(client)
        self.requests = Requests(client)

    def list(self):
        url = self.client.api_url + '/groups'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def get(self, groupId):
        url = self.client.api_url + '/groups/' + groupId
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def create(self, name, description):
        url = self.client.api_url + '/groups'
        method = 'post'
        data = {'name':name, 'description':description}
        return self.client.api_handler(url=url, method=method, data=data)
        
    def update(self, groupId, name, descreption):
        url = self.client.api_url +'/groups/' + groupId
        method = 'put'
        data = {'name':name, 'descreption':descreption}
        return self.client.api_handler(url=url, method=method, data=data)

    def delete(self, groupId):
        url = self.client.api_url +'/groups/' + groupId
        method = 'delete'
        return self.client.api_handler(url=url, method=method)