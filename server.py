import html
import bcrypt
import socketserver
import secrets
import os
import hashlib
from util.websockets import compute_accept
from util.websockets import parse_ws_frame
from util.websockets import generate_ws_frame
from util.multipart import parse_multipart
from util.obj import Obj
from util.part import Part
from util.request import Request
from pymongo import MongoClient
import json
from util.router import Router
from util.auth import extract_credentials
from util.auth import validate_password

websocket_connections = []
online_users = []

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
        message = i.get('message')
        print('image:' + message)
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
    response = 'HTTP/1.1 302 Found\r\n'
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    account_collection = db['account']
    id_collection = db['id']
    ids = id_collection.find_one()
    if ids is None:
        theid = 1
        id_collection.insert_one({'id': 1})
    else:
        theid = ids.get('id') + 1
        id_collection.update_one({}, {'$set': {'id': theid}})
    collection = db['chat']

    for part in info.parts:
        if 'jpg' in part.headers.get('Content-Type') or 'jpeg' in part.headers.get('Content-Type'):
            if 'Content-Disposition' in part.headers:
                original_name = part.headers.get('Content-Disposition')
                original_name = original_name.split(';')
                for name in original_name:
                    if ' filename' in name:
                        name = name.split('=')
                        filename = name[1].strip('/')
                        part.filename = filename
            filename = 'filename_' + str(theid) + '.jpg'
            with open(filename, 'wb') as file:
                file.write(part.content)

            message = '<img src="' + filename + '">'
            if 'auth_token' in request.cookies:
                auth = request.cookies.get('auth_token')
                hashed_auth = hashlib.sha256(auth.encode()).hexdigest()
                check = {'token': hashed_auth}
                document = account_collection.find_one(check)
                if document:
                    if valid_check(hashed_auth, document.get('username')):
                        username = document.get('username')
                        collection.insert_one({'message': message, 'username': username, 'id': theid})
                        break
                    else:
                        collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
                        break
                else:
                    collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
                    break
            else:
                collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
                break
        if 'mp4' in part.headers.get('Content-Type'):
            if 'Content-Disposition' in part.headers:
                original_name = part.headers.get('Content-Disposition')
                original_name = original_name.split(';')
                for name in original_name:
                    if ' filename' in name:
                        name = name.split('=')
                        filename = name[1].strip('/')
                        part.filename = filename
            filename = 'filename_' + str(theid) + '.mp4'
            with open(filename, 'wb') as file:
                file.write(part.content)

            message = '''
            <video width="400" controls autoplay muted>
                <source src="''' + filename + '''" type="video/mp4">
            </video>'''
            if 'auth_token' in request.cookies:
                auth = request.cookies.get('auth_token')
                hashed_auth = hashlib.sha256(auth.encode()).hexdigest()
                check = {'token': hashed_auth}
                document = account_collection.find_one(check)
                if document:
                    if valid_check(hashed_auth, document.get('username')):
                        username = document.get('username')
                        collection.insert_one({'message': message, 'username': username, 'id': theid})
                        break
                    else:
                        collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
                        break
                else:
                    collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
                    break
            else:
                collection.insert_one({'message': message, 'username': 'Guest', 'id': theid})
                break
    response += 'Content-Length: 0; charset=UTF-8\r\nLocation: /'
    return response.encode()

def host_bytes(request: Request):
    filename = request.path[1:]
    with open(filename, 'rb') as file:
        image = file.read()
    response = 'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: image/jpeg; charset=UTF-8\r\n'
    response += 'Content-Length: ' + str(len(image)) + '\r\n\r\n'
    return response.encode() + image





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

def serve_websocket(request: Request, handler):
    mongo_client = MongoClient('mongo')
    db = mongo_client['cse312']
    account_collection = db['account']
    username = 'Guest'
    if 'auth_token' in request.cookies:
        auth = request.cookies.get('auth_token')
        hashed_auth = hashlib.sha256(auth.encode()).hexdigest()
        check = {'token': hashed_auth}
        document = account_collection.find_one(check)
        if document:
            if valid_check(hashed_auth, document.get('username')):
                username = document.get('username')
    print('headers:' + str(request.headers))
    accept = compute_accept(request.headers['Sec-WebSocket-Key'])
    response = b'HTTP/1.1 101 Switching Protocols\r\nX-Content-Type-Options: nosniff\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept: ' + accept.encode() + b'\r\n\r\n'
    handler.request.sendall(response)
    if username != 'Guest':
        if username not in online_users:
            online_users.insert(0, username)
            for self in websocket_connections:
                json_string = json.dumps({'messageType': 'updateUserList', 'username': username})
                frames = generate_ws_frame(json_string.encode())
                self.request.sendall(frames)
    for i in online_users:
        json_string = json.dumps({'messageType': 'updateUserList', 'username': i})
        frames = generate_ws_frame(json_string.encode())
        handler.request.sendall(frames)
    websocket_connections.append(handler)
    received_data = b''
    payload = b''
    payload_length = 0
    while True:
        print('connected')
        continuance = 0
        read_size = 2048
        if len(received_data) == 0:
            received_data = handler.request.recv(read_size)
        print(received_data)
        fin_bit = received_data[0]
        fin_bit = (fin_bit & 128) >> 7
        while fin_bit == 0:
            continuance = 1
            mask = received_data[1]
            mask = (mask & 128) >> 7
            temp = received_data[1]
            temp = temp & 127
            if temp == 126:
                extended_length = received_data[2] << 8 | received_data[3]
                temp = extended_length
            elif temp == 127:
                extended_temp = received_data[2] << 56 | received_data[3] << 48 | received_data[4] << 40 | received_data[5] << 32 | received_data[6] << 24 | received_data[7] << 16 | received_data[8] << 8 | received_data[9]
                temp = extended_temp
            sum = 2
            if mask == 1:
                sum += 4
            if temp >= 126 and temp < 65536:
                sum += 2
            if temp >= 65536:
                sum += 8
            limit = 2048 - sum
            print('limit before:' + str(limit))
            print('temp:'  + str(temp))
            print('actual length:' + str(len(received_data)))
            while temp > limit:
                received_data += handler.request.recv(2048)
                limit = len(received_data)
                limit -= sum
                print('limit after:' + str(limit))
                if len(received_data) == 0:
                    print('NO RECIEVED DATA')
                    break
            frame = parse_ws_frame(received_data)
            print('frame:' + str(frame.payload))
            fin_bit = frame.fin_bit
            temp = frame.payload_length
            temp_payload = frame.payload
            
            if frame.opcode == 1:
                opcode = frame.opcode
            if frame.opcode == 8:
                print('disconnected')
                websocket_connections.remove(handler)
                if username != 'Guest':
                    for self in websocket_connections:
                        json_string = json.dumps({'messageType': 'deleteUserList', 'username': username})
                        frames = generate_ws_frame(json_string.encode())
                        self.request.sendall(frames)
                online_users.remove(username)
                break

            print('fin_bit:')
            print(temp)
            print(len(temp_payload))
            print(len(received_data) - sum)
            current_data = received_data
            if len(received_data) - sum > temp:
                current_data = received_data[:temp + sum]
                received_data = received_data[temp + sum:]
                print('hereee')
            else:
                received_data = b''
            payload_length += temp
            payload += temp_payload
            read_size = 2048
            if len(received_data) == 0:
                received_data = handler.request.recv(read_size)
            print(received_data)
            fin_bit = received_data[0]
            fin_bit = (fin_bit & 128) >> 7

        if continuance == 0:
            read_size = 2048
            if len(received_data) == 0:
                received_data = handler.request.recv(read_size)
            print(received_data)
            mask = received_data[1]
            mask = (mask & 128) >> 7
            payload_length = received_data[1]
            payload_length = payload_length & 127
            if payload_length == 126:
                extended_length = received_data[2] << 8 | received_data[3]
                payload_length = extended_length
            elif payload_length == 127:
                extended_payload_length = received_data[2] << 56 | received_data[3] << 48 | received_data[4] << 40 | received_data[5] << 32 | received_data[6] << 24 | received_data[7] << 16 | received_data[8] << 8 | received_data[9]
                payload_length = extended_payload_length
            sum = 2
            if mask == 1:
                sum += 4
            if payload_length >= 126 and payload_length < 65536:
                sum += 2
            if payload_length >= 65536:
                sum += 8
            limit = 2048 - sum
            print('limit before:' + str(limit))
            print('payload_length:'  + str(payload_length))
            print('actual length:' + str(len(received_data)))
            while payload_length > limit:
                received_data += handler.request.recv(2048)
                limit = len(received_data)
                limit -= sum
                print('limit after:' + str(limit))
                if len(received_data) == 0:
                    print('NO RECIEVED DATA')
                    break
            frame = parse_ws_frame(received_data)
            print('frame:' + str(frame.payload))
            fin_bit = frame.fin_bit
            payload_length = frame.payload_length
            payload = frame.payload
                
            if frame.opcode == 1:
                opcode = frame.opcode
            if frame.opcode == 8:
                print('disconnected')
                websocket_connections.remove(handler)
                if username != 'Guest':
                    for self in websocket_connections:
                        json_string = json.dumps({'messageType': 'deleteUserList', 'username': username})
                        frames = generate_ws_frame(json_string.encode())
                        self.request.sendall(frames)
                online_users.remove(username)
                break

            print('fin_bit:')
            print(payload_length)
            print(len(payload))
            print(len(received_data) - sum)
            current_data = received_data
            if len(received_data) - sum > payload_length:
                current_data = received_data[:payload_length + sum]
                received_data = received_data[payload_length + sum:]
                print('hereee')
            else:
                received_data = b''
        else:
            mask = received_data[1]
            mask = (mask & 128) >> 7
            temp_payload_length = received_data[1]
            temp_payload_length = temp_payload_length & 127
            if temp_payload_length == 126:
                extended_length = received_data[2] << 8 | received_data[3]
                temp_payload_length = extended_length
            elif temp_payload_length == 127:
                extended_payload_length = received_data[2] << 56 | received_data[3] << 48 | received_data[4] << 40 | received_data[5] << 32 | received_data[6] << 24 | received_data[7] << 16 | received_data[8] << 8 | received_data[9]
                temp_payload_length = extended_payload_length
            sum = 2
            if mask == 1:
                sum += 4
            if temp_payload_length >= 126 and temp_payload_length < 65536:
                sum += 2
            if temp_payload_length >= 65536:
                sum += 8
            limit = 2048 - sum
            print('limit before:' + str(limit))
            print('payload_length:'  + str(temp_payload_length))
            print('actual length:' + str(len(received_data)))
            while temp_payload_length > limit:
                received_data += handler.request.recv(2048)
                limit = len(received_data)
                limit -= sum
                print('limit after:' + str(limit))
                if len(received_data) == 0:
                    print('NO RECIEVED DATA')
                    break
            frame = parse_ws_frame(received_data)
            print('frame:' + str(frame.payload))
            fin_bit = frame.fin_bit
            temp_payload_length = frame.payload_length
            temp_payload = frame.payload
                
            if frame.opcode == 1:
                opcode = frame.opcode
            if frame.opcode == 8:
                print('disconnected')
                websocket_connections.remove(handler)
                if username != 'Guest':
                    for self in websocket_connections:
                        json_string = json.dumps({'messageType': 'deleteUserList', 'username': username})
                        frames = generate_ws_frame(json_string.encode())
                        self.request.sendall(frames)
                online_users.remove(username)
                break

            print('fin_bit:')
            print(temp_payload_length)
            print(len(temp_payload))
            print(len(received_data) - sum)
            current_data = received_data
            if len(received_data) - sum > temp_payload_length:
                current_data = received_data[:temp_payload_length + sum]
                received_data = received_data[temp_payload_length + sum:]
                print('hereee')
            else:
                received_data = b''
            payload_length += temp_payload_length
            payload += temp_payload
            print(len(payload))
            print(payload_length)

        



        
        if opcode == 1:
            string = json.loads(payload.decode())
            mongo_client = MongoClient('mongo')
            db = mongo_client['cse312']
            chat_collection = db['chat']
            id_collection = db['id']
            ids = id_collection.find_one()
            if ids is None:
                theid = 1
                id_collection.insert_one({'id': 1})
            else:
                theid = ids.get('id') + 1
                id_collection.update_one({}, {'$set': {'id': theid}})
            message = html.escape(string['message'])
            chat_collection.insert_one({'message': message, 'username': username, 'id': theid})
            json_string = json.dumps({'messageType': string['messageType'], 'username': username, 'message': message, 'id': theid})
            frames = generate_ws_frame(json_string.encode())
            for self in websocket_connections:
                self.request.sendall(frames)


            payload = b''
            payload_length = 0





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
router.add_route('GET', '/filename_.', host_bytes)
router.add_route('GET', '/websocket$', serve_websocket)


class MyTCPHandler(socketserver.BaseRequestHandler):

    #for router add make sure the ones needed to run before get added first before the all like .js


    def handle(self):
        received_data = self.request.recv(2048)
        request = Request(received_data)
        if 'Content-Length' in request.headers:
            content_length = int(request.headers['Content-Length'])
        else:
            content_length = 0
        data_size = len(received_data)
        while content_length > data_size:
            received_data += self.request.recv(2048)
            data_size = len(received_data)
            if len(received_data) == 0:
                break

        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        response = router.route_request(request, self)
        self.request.sendall(response)


    # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response



def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
