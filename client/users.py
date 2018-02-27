class Users:
    def __init__(self, client):
        self.client = client

    def search(self, string):
        url = self.client.api_url + '/users/search?q=' + string
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def getAuthUser(self):
        url = self.client.api_url + '/user'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def getNotifications(self):
        url = self.client.api_url + '/user/notifications'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def getUser(self, username):
        url = self.client.api_url + '/users/' + username
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def getUserNotifications(self):
        url = self.client.api_url + '/user/notifications'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def updateName(self, firstname, lastname):
        url = self.client.api_url +'/user/name'
        method = 'put'
        data = {'firstname':firstname, 'lastname':lastname}
        return self.client.api_handler(url=url, method=method, data=data)

    def updateEmail(self, email):
        url = self.client.api_url +'/user/email'
        method = 'put'
        data = {'email':email}
        return self.client.api_handler(url=url, method=method, data=data)

    def updatePassword(self, old_password, new_password):
        url = self.client.api_url +'/user/password'
        method = 'put'
        data = {'old_password':old_password, 'new_password':new_password}
        return self.client.api_handler(url=url, method=method, data=data)