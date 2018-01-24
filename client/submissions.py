class Submissions:
    def __init__(self, client):
        self.client = client

    def list(self, groupId, assignmentId):
        url = self.client.api_url + '/groups/' + groupId + '/assignments/' + assignmentId + '/submissions'
        method = 'get'
        return self.client.api_handler(url=url, method=method)

    def get(self, submissionId):
        url = self.client.api_url + '/submissions/' + submissionId
        method = 'get'
        return self.client.api_handler(url=url, method=method)
