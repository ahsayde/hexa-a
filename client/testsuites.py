class Testsuites:
    def __init__(self, client):
        self.client = client

    def list(self, groupId):
        url = self.client.api_url + '/groups/' + groupId + '/testsuites'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def get(self, groupId, testsuiteId):
        url = self.client.api_url + '/groups/' + groupId + '/testsuites/' + testsuiteId
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def getSuggestedTestcases(self, groupId, testsuiteId):
        url = self.client.api_url + '/groups/' + groupId + '/testsuites/' + testsuiteId + '/testcases/suggested'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def create(self, groupId, name, description, level, testcases):
        url = self.client.api_url + '/groups/' + groupId + '/testsuites'
        method = 'post'
        data = {'name':name, 'description':description, "level":level, 'testcases':testcases}
        return self.client.api_handler(url=url, method=method, data=data)
        
    def update(self, groupId, testsuiteId, name, descreption, level, testcases):
        url = self.client.api_url + '/groups/' + groupId + '/testsuites/' + testsuiteId
        method = 'put'
        data = {'name':name, 'descreption':descreption, "level":level, 'testcases':testcases}
        return self.client.api_handler(url=url, method=method, data=data)

    def delete(self, groupId, testsuiteId):
        url = self.client.api_url + '/groups/' + groupId + '/testsuites/' + testsuiteId
        method = 'delete'
        return self.client.api_handler(url=url, method=method)
