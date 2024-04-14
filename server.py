import html
import bcrypt
import socketserver
import secrets
import os
import hashlib
from util.multipart import parse_multipart
from util.obj import Obj
from util.part import Part
from util.request import Request
from pymongo import MongoClient
import json
from util.router import Router
from util.auth import extract_credentials
from util.auth import validate_password

def serve_html(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/html; charset=UTF-8\r\n'
    path = request.path[1:]
    f = open(path, "rb")
    body = f.read()
    response += 'Content-Length: ' + str(len(body)) + '\r\n\r\n'
    return response.encode() + body

def serve_js(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/javascript; charset=UTF-8\r\n'
    path = request.path[1:]
    f = open(path, "rb")
    body = f.read()
    response += 'Content-Length: ' + str(len(body)) + '\r\n\r\n'
    return response.encode() + body

def serve_css(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/css; charset=UTF-8\r\n'
    path = request.path[1:]
    f = open(path, "rb")
    body = f.read()
    response += 'Content-Length: ' + str(len(body)) + '\r\n\r\n'
    return response.encode() + body

def serve_ico(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: image/x-icon; charset=UTF-8\r\n'
    path = request.path[1:]
    f = open(path, "rb")
    body = f.read()
    response += 'Content-Length: ' + str(len(body)) + '\r\n\r\n'
    return response.encode() + body

def serve_jpg(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: image/jpeg; charset=UTF-8\r\n'
    path = request.path[1:]
    f = open(path, "rb")
    body = f.read()
    response += 'Content-Length: ' + str(len(body)) + '\r\n\r\n'
    return response.encode() + body

def serve_json(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: application/json; charset=UTF-8\r\n'
    path = request.path[1:]
    f = open(path, "rb")
    body = f.read()
    response += 'Content-Length: ' + str(len(body)) + '\r\n\r\n'
    return response.encode() + body

def serve_png(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: image/png; charset=UTF-8\r\n'
    path = request.path[1:]
    f = open(path, "rb")
    body = f.read()
    response += 'Content-Length: ' + str(len(body)) + '\r\n\r\n'
    return response.encode() + body

def serve_txt(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\n'
    path = request.path[1:]
    f = open(path, "rb")
    body = f.read()
    response += 'Content-Length: ' + str(len(body)) + '\r\n\r\n'
    return response.encode() + body

def serve_main(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
    visits = 1
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    account_collection = db['account']

    if 'visits' in request.cookies:
        visits = int(request.cookies.get('visits'))
        visits += 1
        response += 'Set-Cookie: visits=' + str(visits) + '; Max-Age=7200\r\n'
    else:
        response += 'Set-Cookie: visits=1; Max-Age=7200\r\n'
    response += 'Content-Type: text/html; charset=UTF-8\r\n'
    f = open("public/index.html", "rb")
    body = f.read()
    stringbody = body.decode()
    stringbody = stringbody.replace('{{visits}}', str(visits))
    stringbody = stringbody.replace('{{visits}}', str(visits))
    if 'auth_token' in request.cookies:
        auth = request.cookies.get('auth_token')
        hashed_auth = hashlib.sha256(auth.encode()).hexdigest()
        check = {'token': hashed_auth}
        document = account_collection.find_one(check)
        if document:
            if valid_check(hashed_auth, document.get('username')):
                if 'xsrf-value' in stringbody:
                    token = secrets.token_hex(16)
                    account_collection.update_one(document, {'$set': {'xsrf': token}})
                    stringbody = stringbody.replace('xsrf-value', token)
    response += 'Content-Length: ' + str(len(stringbody)) + '\r\n\r\n'
    response += stringbody
    return response.encode()

def serve_chat_post(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
    response += 'Content-Type: text/plain; charset=UTF-8\r\n'
    response += 'Content-Length: 0; charset=UTF-8\r\n\r\n'
    data = json.loads(request.body)
    message = data['message']
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    chat_collection = db['chat']
    id_collection = db['id']
    account_collection = db['account']
    ids = id_collection.find_one()
    if ids is None:
        theid = 1
        id_collection.insert_one({'id': 1})
    else:
        theid = ids.get('id') + 1
        id_collection.update_one({}, {'$set': {'id': theid}})
    if 'auth_token' in request.cookies:
        auth = request.cookies.get('auth_token')
        hashed_auth = hashlib.sha256(auth.encode()).hexdigest()
        check = {'token': hashed_auth}
        document = account_collection.find_one(check)
        if document:
            if valid_check(hashed_auth, document.get('username')):
                if 'xsrf' in data:
                    xsrf = data['xsrf']
                    if document.get('xsrf') == xsrf:
                        username = document.get('username')
                        chat_collection.insert_one({'message': message, 'username': username, 'id': theid})
                    else:
                        return b"HTTP/1.1 403 Forbidden\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 46\r\n\r\nYou don't have permission to access this resource"
                else:
                    return b"HTTP/1.1 403 Forbidden\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 46\r\n\r\nYou don't have permission to access this resource"
            else:
                chat_collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
        else:
            chat_collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
    else:
        chat_collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
    return response.encode()

def serve_chat_get(request: Request):
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\n'
    response += 'Content-Type: application/json; charset=UTF-8\r\n'
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    chat_collection = db['chat']
    chats = chat_collection.find({})
    chat_list = [{}]
    for i in chats:
        message = html.escape(i.get('message'))
        chat_list.append({'message': message, 'username': i.get('username'), 'id': i.get('id')})

    body = json.dumps(chat_list)
    response += 'Content-Length: ' + str(len(body.encode())) + '\r\n\r\n'
    return response.encode() + body.encode()

def serve_registration(request: Request):
    response = 'HTTP/1.1 302 Found\r\n'
    response += 'Content-Length: 0; charset=UTF-8\r\n'
    response += 'Location: /'
    data = extract_credentials(request)
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    collection = db['account']
    password = data[1]
    if validate_password(password):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        collection.insert_one({'username': data[0], 'password': hashed_password})
    return response.encode()

def serve_login(request: Request):
    response = 'HTTP/1.1 302 Found\r\n'
    response += 'Content-Length: 0; charset=UTF-8\r\n'
    data = extract_credentials(request)
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    valid_collection = db['valid']
    collection = db['account']
    user = {'username': data[0]}
    document = collection.find_one(user)
    if document:
        password = document.get('password')
        if bcrypt.checkpw(data[1].encode(), password):
            auth = secrets.token_hex(20)
            hashed_auth = hashlib.sha256(auth.encode()).hexdigest()
            collection.update_one(document, {'$set': {'token': hashed_auth}})
            valid_collection.insert_one({'token': hashed_auth, 'valid': True})
            response += 'Set-Cookie: auth_token=' + auth + '; Max-Age=7200; HttpOnly\r\n'
    response += 'Location: /'
    return response.encode()

def serve_logout(request: Request):
    response = 'HTTP/1.1 302 Found\r\n'
    response += 'Content-Length: 0; charset=UTF-8\r\n'
    token = request.cookies.get('auth_token')
    hashed_auth = hashlib.sha256(token.encode()).hexdigest()
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    valid_collection = db['valid']
    valid = {'token': hashed_auth}
    document = valid_collection.find_one(valid)
    if document:
        valid_collection.update_one(document, {'$set': {'valid': False}})
    request.cookies.pop('auth_token')
    response += 'Location: /'
    return response.encode()

def serve_upload(request: Request):
    info = parse_multipart(request)
    i = 1
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    collection = db['chat']
    if os.path.exists('filename.jpg'):
        while os.path.exists('filename' + str(i) + '.jpg'):
            i += 1
        with open('filename' + str(i) + '.jpg', 'w') as file:
            if len(info.parts) > 0:
                file.write(info.parts[len(info.parts) - 1].content)
            collection.insert_one({'name': 'filename' + str(i) + '.jpg'})
    else:
        with open('filename.jpg', 'w') as file:
            if len(info.parts) > 0:
                file.write(info.parts[len(info.parts) - 1].content)
            collection.insert_one({'name': 'filename.jpg'})
    response = 'HTTP/1.1 302 Found\r\n'
    response += 'Content-Length: 0; charset=UTF-8\r\nLocation: /'
    return response.encode()




def serve_delete(request: Request):
    path = request.path[1:]
    message_id = ''
    count = False
    for i in path:
        if count == True and i != ' ':
            message_id += i
        if i == '/':
            count = True
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    chat_collection = db['chat']
    check = {'id': int(message_id)}
    document = chat_collection.find_one(check)
    token = request.cookies.get('auth_token')
    if document:
        hashed_auth = hashlib.sha256(token.encode()).hexdigest()
        if valid_check(hashed_auth, document.get('username')):
            chat_collection.delete_one(document)
            return b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0; charset=UTF-8'
    return b"HTTP/1.1 403 Forbidden\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 46\r\n\r\nYou don't have permission to access this resource"




def valid_check(hashed_auth, username: str):
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    collection = db['valid']
    account_collection = db['account']
    check = {'token': hashed_auth}
    document = collection.find_one(check)
    account_document = account_collection.find_one(check)
    if document and account_document:
        if document.get('valid') and username == account_document.get('username'):
            return True
    return False




router = Router()
router.add_route('GET', '/public/functions.js$', serve_js)
router.add_route('GET', '/public/favicon.ico$', serve_ico)
router.add_route('GET', '/public/index.html$', serve_main)
router.add_route('GET', '/public/style.css$', serve_css)
router.add_route('GET', '/public/webrtc.js$', serve_js)
router.add_route('GET', '/public/image/.', serve_jpg)
router.add_route('GET', '/$', serve_main)
router.add_route('GET', '/chat-messages$', serve_chat_get)
router.add_route('POST', '/chat-messages$', serve_chat_post)
router.add_route('POST', '/chat-messages$', serve_chat_post)
router.add_route('POST', '/login$', serve_login)
router.add_route('POST', '/register$', serve_registration)
router.add_route('POST', '/logout$', serve_logout)
router.add_route('DELETE', '/chat-messages/.', serve_delete)
router.add_route('POST', '/image_upload$', serve_upload)


class MyTCPHandler(socketserver.BaseRequestHandler):

    #for router add make sure the ones needed to run before get added first before the all like .js


    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        response = router.route_request(request)
        self.request.sendall(response)




    # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response



def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
