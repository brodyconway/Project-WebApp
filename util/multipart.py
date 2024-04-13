from util.request import Request
from util.obj import Obj
from util.part import Part


def parse_multipart(request: Request):
    content_length = request.headers['Content-Length']
    body = request.body
    content_type = request.headers['Content-Type']
    boundary = content_type.split('=')[1]
    byte_boundary = boundary.encode()
    parts = []
    new_line = '\r\n\r\n'.encode()
    x = 1
    while True:
        keys = {}
        new = body.split('--'.encode() + byte_boundary)
        if new[x][:2] == '--'.encode():
            break
        next = new[x][2:]
        next = next.split(new_line)
        headers = next[0]
        content = b''
        if len(next) > 2:
            i = 1
            while len(next) > i:
                if i != 1:
                    content += b'\r\n\r\n'
                if i + 1 == len(next):
                    content += next[i][:-2]
                    i += 1
                else:
                    content += next[i]
                    i += 1
        else:
            content = next[1][:-2]
        headers = headers.split(b'\r\n')
        i = 0
        while i < len(headers):
            key = headers[i].split(b':')
            keys[key[0].decode()] = key[1][1:].decode()
            i += 1
        name = ''
        content_disposition = keys['Content-Disposition']
        content_disposition = content_disposition.split(';')
        for t in content_disposition:
            if 'name=' in t:
                temp = t.split('=')
                name = temp[1]
                name = name[1:]
                name = name[:(len(name) - 1)]
                break
        part = Part(keys, name, content)
        parts.append(part)
        x += 1
    done = Obj(boundary, parts)
    return done

def test1():
    request = Request(b'POST /form-path HTTP/1.1\r\nContent-Length: 9937\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n\r\ntest\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="upload"; filename="discord.png"\r\nContent-Type: image/png\r\n\r\nbytesoffile\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--')
    multipart = parse_multipart(request)
    headers = {'Content-Disposition': 'form-data; name="commenter"'}
    parts = Part(headers, 'commenter', b'Jesse')
    part = Part(headers, 'commenter', b'Jesse')
    assert(multipart.getBoundary() == '----WebKitFormBoundarycriD3u6M0UuPR1ia')


if __name__ == '__main__':
    test1()

        
        

    
