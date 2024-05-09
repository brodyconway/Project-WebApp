import re
from util.request import Request

class Router:
    def __init__(self):
        self.add = []
    def add_route(self, httpMethod: str, path: str, request):
            self.add.append([path, httpMethod, request])

    def route_request(self, request: Request, handler):
        for i in self.add:
            match = re.match(i[0], request.path)
            match2 = re.match(i[1], request.method)
            if match and match2:
                if i[0] == '/websocket$':
                     return i[2](request, handler)
                print('test:' + str(i[0]))
                return i[2](request)
        return b'HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 36\r\n\r\nThe requested content does not exist'