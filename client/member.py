class Members:
    def __init__(self, client):
        self.client = client

    def list(self, groupId):
        url = self.client.api_url + '/groups/' + groupId + '/members'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def add(self, groupId, member, role='member'):
        url = self.client.api_url + '/groups/' + groupId + '/members'
        method = 'post'
        data = {'member':member, 'role':role}
        return self.client.api_handler(url=url, method=method, data=data)

    def update(self, groupId, member, role):
        url = self.client.api_url + '/groups/' + groupId + '/members/' + member
        method = 'put'
        data = {'role':role}
        return self.client.api_handler(url=url, method=method, data=data)

    def remove(self, groupId, member):
        url = self.client.api_url + '/groups/' + groupId + '/members/' + member
        method = 'delete'
        return self.client.api_handler(url=url, method=method)
