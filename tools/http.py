from flask import Response

class HttpResponse:

    def sendResponse(self, status, msg, content_type=None):
        return Response(msg, status=status, mimetype=content_type)

    def Ok(self, msg=None):
        return self.sendResponse(status=200, msg=msg, content_type='application/json')

    def Created(self, msg=None):
        return self.sendResponse(status=201, msg=msg)

    def NoContent(self, msg=None):
        return self.sendResponse(status=204, msg=msg)

    def BadRequest(self, msg='Bad Request'):
        return self.sendResponse(status=400, msg=msg)

    def NotFound(self, msg='Not Found'):
        return self.sendResponse(status=404, msg=msg)

    def Conflict(self, msg='Conflict'):
        return self.sendResponse(status=409, msg=msg)

    def InternalServerError(self, msg='Internal Server Error'):
        return self.sendResponse(status=500, msg=msg)

    def Forbidden(self, msg='Forbidden'):
        return self.sendResponse(status=403, msg=msg)

    def Unauthorized(self, msg='Unauthorized'):
        return self.sendResponse(status=401, msg=msg)
