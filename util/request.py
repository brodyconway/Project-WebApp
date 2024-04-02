class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables

        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}
        s = ""
        i = chr(request[0])
        t = 0
        n = 0
        while i != '\r' and i != '\n':
            while i != ' ' and i != '\r':
                s = s + i
                t = t + 1
                if t >= len(request):
                    break
                i = chr(request[t])
            if n == 0:
                self.method = s
            elif n == 1:
                self.path = s
            else:
                self.http_version = s
            n = n + 1
            t = t + 1
            if t < len(request):
                i = chr(request[t])
            s = ""
        n = 0
        while True:
            s = ""
            key = ""
            endcheck = ""
            while i == '\r' or i == '\n':
                endcheck = endcheck + i
                t = t + 1
                if t >= len(request):
                    break
                i = chr(request[t])
            if '\r\n\r\n' in endcheck:
                break
            while i != ':':
                key = key + i
                t = t + 1
                if t >= len(request):
                    break
                i = chr(request[t])
            if key == 'Cookie':
                l = t
                while i != '\r' and i != '\n':
                    while i == ' ' or i == ':' or i == ';':
                        l = l + 1
                        if l >= len(request):
                            break
                        i = chr(request[l])
                    cookiekey = ""
                    v = ""
                    while i != '=':
                        cookiekey = cookiekey + i
                        l = l + 1
                        if l >= len(request):
                            break
                        i = chr(request[l])
                    l = l + 1
                    if l >= len(request):
                        break
                    i = chr(request[l])
                    while i != ';' and i != '\r' and i != '\n':
                        v = v + i
                        l = l + 1
                        if l >= len(request):
                            break
                        i = chr(request[l])
                    self.cookies[cookiekey] = v
            i = chr(request[t])
            while i == ' ' or i == ':':
                t = t + 1
                if t >= len(request):
                    break
                i = chr(request[t])
            while i != '\r' and i != '\n':
                s = s + i
                t = t + 1
                if t >= len(request):
                    break
                i = chr(request[t])
            self.headers[key] = s
        if(t < len(request)):
            self.body = request[t:]
















def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct
def test2():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nCookie: id=X6kA; id2=24556; username=brody; password=hello\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.headers["Cookie"] == 'id=X6kA; id2=24556; username=brody; password=hello'
    assert request.body == b""
    assert request.cookies['id'] == 'X6kA'
    assert request.cookies['id2'] == '24556'
    assert request.cookies['username'] == 'brody'
    assert request.cookies['password'] == 'hello'

if __name__ == '__main__':
    test1()
    test2()
