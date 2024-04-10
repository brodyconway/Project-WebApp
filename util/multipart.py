from util.request import Request
from util.obj import Obj
from util.part import Part

def parse_multipart(request: Request):
    content_length = request.headers['Content-Length']
    body = request.body
    content_type = request.headers['Content-Type']
    boundary = content_type.split('=')[1]
    byte_boundary = boundary.encode()
    done = Obj(boundary, None)
    parts = []
    new_line = '\r\n\r\n'.encode()
    x = 1
    while True:
        keys = {}
        new = body.split('--'.encode() + byte_boundary)
        if new[x][:2]== '--'.encode():
            break
        next = new[x][2:]
        next = next.split('\r\n\r\n'.encode())
        headers = next[0]
        content = next[1]
        headers = headers.split(':'.encode())
        i = 0
        while headers[i]:
            if headers[i + 1]:
                keys[headers[i]] = headers[i + 1]
            else:
                keys[headers[i]] = None
            i += 2
        name = b''
        content_diposition = keys['Content-Diposition'.encode()]
        content_diposition = content_diposition.split(';'.encode())
        for t in content_diposition:
            if 'name='.encode() in t:
                temp = t.split('='.encode())
                name = temp[1]
                break
        part = Part(keys, name, content)
        parts.append(part)
        x += 1





        
        

    
