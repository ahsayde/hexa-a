class Announcements:
    def __init__(self, client):
        self.client = client

    def list(self, groupId):
        url = self.client.api_url + '/groups/' + groupId + '/announcements'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def create(self, groupId, content):
        url = self.client.api_url + '/groups/' + groupId + '/announcements'
        method = 'post'
        data = {'content':content}
        return self.client.api_handler(url=url, method=method, data=data)
        
    def update(self, groupId, announcementId, content):
        url = self.client.api_url + '/groups/' + groupId + '/announcements/' + announcementId
        method = 'put'
        data = {'content':content}
        return self.client.api_handler(url=url, method=method, data=data)

    def delete(self, groupId, announcementId):
        url = self.client.api_url + '/groups/' + groupId + '/announcements/' + announcementId
        method = 'delete'
        return self.client.api_handler(url=url, method=method)