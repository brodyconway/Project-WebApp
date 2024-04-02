from util.request import Request

def extract_credentials(request: Request):
    list = []
    body = request.body.decode()
    char = body[0]
    i = 1
    while char != '=':
        char = body[i]
        i += 1
    username = ''
    while char != '&':
        char = body[i]
        if char != '&':
            username += char
        i += 1
    while char != '=':
        char = body[i]
        i += 1
    password = ''
    while i < len(body):
        char = body[i]
        if char == '%':
            char = body[i]
            temp = body[i + 1] + body[i + 2]
            i += 3
            if temp == '21':
                password += '!'

            if temp == '40':
                password += '@'
            if temp == '23':
                password += '#'
            if temp == '24':
                password += '$'
            if temp == '25':
                password += '%'
            if temp == '5E':
                password += '^'
            if temp == '26':
                password += '&'
            if temp == '28':
                password += '('
            if temp == '29':
                password += ')'
            if temp == '2D':
                password += '-'
            if temp == '5F':
                password += '_'
            if temp == '3D':
                password += '='
        else:
            i += 1
            password += char
    list.append(username)
    list.append(password)
    return list

def validate_password(s: str):
    lowercase = False
    uppercase = False
    number = False
    special = False
    if len(s) < 8:
        return False
    for i in s:
        valid = False
        if i.islower():
            lowercase = True
        if i.isupper():
            uppercase = True
        if i.isdigit():
            number = True
        if i == '!':
            special = True
            valid = True
        if i == '@':
            special = True
            valid = True
        if i == '#':
            special = True
            valid = True
        if i == '$':
            special = True
            valid = True
        if i == '%':
            special = True
            valid = True
        if i == '^':
            special = True
            valid = True
        if i == '&':
            special = True
            valid = True
        if i == '(':
            special = True
            valid = True
        if i == ')':
            special = True
            valid = True
        if i == '-':
            special = True
            valid = True
        if i == '_':
            special = True
            valid = True
        if i == '=':
            special = True
            valid = True
        if not i.isalnum() and not valid:
            return False
    if lowercase and uppercase and number and special:
        return True
    else:
        return False


def test():
    request = Request(b'POST / HTTP/1.1\r\nHost: localhost:8080\r\n\r\nusername=brody&password=123rt%21')

    extract = extract_credentials(request)
    assert extract[0] == 'brody'
    assert extract[1] == '123rt!'

def test2():
    s = 'hello%90'
    check = validate_password(s)
    assert not check
    s = 'hello'
    check = validate_password(s)
    assert not check

    s = 'He$@l89^'
    check = validate_password(s)
    assert check

    s = 'helloI42*$'
    check = validate_password(s)
    assert not check

    s = 'helloLJ534'
    check = validate_password(s)
    assert not check

    s = '534535535'
    check = validate_password(s)
    assert not check

    s = 'helloLJ534'
    check = validate_password(s)
    assert not check

if __name__ == '__main__':
    test()
    test2()