class Authentication:
    def __init__(self, client):
        self.client = client

    def get_access_token(self, login, password):
        url = self.client.base_url + '/auth'
        method = 'post'
        params = {'login':login, 'password':password}
        return self.client.api_handler(url=url, method=method, params=params)
