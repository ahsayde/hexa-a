class Assignments:
    def __init__(self, client):
        self.client = client

    def list(self, groupId):
        url = self.client.api_url + '/groups/' + groupId + '/assignments'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def get(self, groupId, assignmentId):
        url = self.client.api_url + '/groups/' + groupId + '/assignments/' + assignmentId
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def create(self, groupId, name, description):
        url = self.client.api_url + '/groups/' + groupId + '/assignments'
        method = 'post'
        data = {'name':name, 'description':description}
        return self.client.api_handler(url=url, method=method, data=data)
        
    def update(self, groupId, assignmentId, name, descreption):
        url = self.client.api_url + '/groups/' + groupId + '/assignments/' + assignmentId
        method = 'put'
        data = {'name':name, 'descreption':descreption}
        return self.client.api_handler(url=url, method=method, data=data)

    def delete(self, groupId, assignmentId):
        url = self.client.api_url + '/groups/' + groupId + '/assignments/' + assignmentId
        method = 'delete'
        return self.client.api_handler(url=url, method=method)

    def linkTestsuite(self, groupId, assignmentId, testsuiteId):
        url = self.client.api_url + '/groups/' + groupId + '/assignments/' + assignmentId + '/testsuites'
        method = 'post'
        data = {'testsuiteId':testsuiteId}
        return self.client.api_handler(url=url, method=method, data=data)

    def unlinkTestsuite(self, groupId, assignmentId, testsuiteId):
        url = self.client.api_url + '/groups/' + groupId + '/assignments/' + assignmentId + '/testsuites/' + testsuiteId
        method = 'delete'
        return self.client.api_handler(url=url, method=method)

    def submissions(self, groupId, assignmentId, params=None):
        url = self.client.api_url + '/groups/' + groupId + '/assignments/' + assignmentId + '/submissions'
        method = 'get'
        return self.client.api_handler(url=url, method=method, params=params)

        