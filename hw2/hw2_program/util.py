import random
import json

def encode_dict(packet):
    """
    For use with sending a packet over the wire.
    """
    packet = json.dumps(packet)
    packet = packet.encode('ascii')
    return packet

def decode_dict(packet):
    """
    For use with recv'ing a packet over the wire.
    """
    packet = packet.decode('ascii')
    packet = json.loads(packet)
    return packet

def gen_nonce():
    return random.getrandbits(10)

def parse_secret_key(key_num, key_letter):
    key_num_domain = [0, 1, 2, 3]

    if int(key_num) not in key_num_domain:
        print("key_num should be 0, 1, 2, or 3")
        sys.exit()

    if len(key_letter) != 1:
        print("key_letter should only be one character")
        sys.exit()

    key = (int(key_num) << 8) | ord(key_letter)

    return key
