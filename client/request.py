class Requests:
    def __init__(self, client):
        self.client = client

    def list(self, groupId):
        url = self.client.api_url + '/groups/' + groupId + '/requests'
        method = 'get'
        return self.client.api_handler(url=url, method=method)
