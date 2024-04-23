import hashlib
import base64
from util.frame import Frame

def compute_accept(key: str):
    guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    key += guid
    key = base64.b64encode(hashlib.sha1(key.encode()).hexdigest())
    print(key)
    return key

def parse_ws_frame(frame):
    opcode = frame[0]
    opcode = opcode & 15
    opcode = int(opcode)
    fin_bit = frame[0]
    fin_bit = fin_bit & 128
    fin_bit = int(fin_bit)
    mask = frame[1]
    mask = mask & 128
    mask = int(mask)
    payload_length = frame[1]
    payload_length = payload_length & 127
    payload_length = int(payload_length)
    current_frame = 2
    if payload_length == 126:
        current_frame = 4
        extended = frame[2]
        extended += frame[3]
        extended = int(extended)
        payload_length = extended
    elif payload_length == 127:
        current_frame = 10
        extended = frame[2]
        extended += frame[3]
        extended += frame[4]
        extended += frame[5]
        extended += frame[6]
        extended += frame[7]
        extended += frame[8]
        extended += frame[9]
        payload_length = extended

    if mask == 1:
        m = [frame[current_frame], frame[current_frame + 1], frame[current_frame + 2], frame[current_frame + 3]]
        current_frame += 4
        i = 0
        payload = b''
        while i < payload_length:
            payload += frame[current_frame + i] ^ m[i % 4]
            i += 1
        return Frame(fin_bit, opcode, payload_length, payload)
    else:
        payload = b''
        i = 0
        while i < payload_length:
            payload += frame[current_frame + i]
            i += 1
        return Frame(fin_bit, opcode, payload_length, payload)

def generate_ws_frame(payload):
    frame = '100000010'
    length = len(payload)
    if length < 126:
        length = str(bin(length))
        frame += length
        return frame.encode() + payload
    elif 126 <= length < 65536:
        add = str(bin(126))
        frame += add
        length = str(bin(length))
        frame += length
        return frame.encode() + payload
    elif length >= 65536:
        add = str(bin(127))
        frame += add
        length = str(bin(length))
        frame += length
        return frame.encode() + payload


def test1():
    return


if __name__ == '__main__':
    compute_accept('ghdjkksjgj3')