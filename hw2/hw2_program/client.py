import socket
import sys
import json
import time

from toy_des import ToyDES
from util import encode_dict, decode_dict, gen_nonce

class Client:
    def __init__(self, p, g, secret_a, user):
        """
        Upon client initialization, connects to the KDC.
        """
        self.kdc_address_1 = ('localhost', 42011)
        self.kdc_address_2 = ('localhost', 42009)
        self.alice_address_1 = ('localhost', 42010)
        self.bob_address = ('localhost', 42012)
        self.bob_address_2 = ('localhost', 42013)
        self.alice_address_2 = ('localhost', 42014)

        self.p = p
        self.g = g
        self.secret_a = secret_a
        self.user = user

    def connect_to_KDC(self):
        self.kdc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.user == "alice":
            self.kdc_sock.bind(self.alice_address_1)
        else:
            self.kdc_sock.bind(self.bob_address)
        self.kdc_sock.connect(self.kdc_address_1)

    def close_connection_to_KDC(self):
        self.kdc_sock.close()

    def send_nonce_to_alice(self):
        self.replay_nonce = gen_nonce()
        des = ToyDES(self.secret_s)
        encrypted_nonce = des.encrypt(self.replay_nonce)
        packet = {'nonce_b_e': encrypted_nonce}
        packet = encode_dict(packet)

        self.nonce_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nonce_sock.connect(self.alice_address_2)

        self.nonce_sock.sendall(packet)
        self.nonce_sock.close()

    def get_nonce_from_bob(self):
        self.nonce_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nonce_sock.bind(self.alice_address_2)
        self.nonce_sock.listen(1)
        print("Waiting for Bob's nonce at", self.alice_address_2)

        self.nonce_connection, self.nonce_address = self.nonce_sock.accept()
        print("Bob connected")
        packet = self.nonce_connection.recv(1024)
        packet = decode_dict(packet)
        self.nonce_b_e = packet['nonce_b_e']

    def wait_for_NS(self):
        """
        Alice will use this method to wait for KDC to initiate NS process
        """
        self.kdc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Waiting for KDC at", self.alice_address_1)
        self.kdc_sock.bind(self.alice_address_1)
        self.kdc_sock.listen(1)

        self.kdc_connection, self.kdc_address = self.kdc_sock.accept()
        print("KDC connected")

    def start_NS(self):
        nonce_a = gen_nonce()
        packet = {'user1': "alice", 'user2': "bob", 'nonce_a': nonce_a, 'nonce_b_e': self.nonce_b_e}
        packet = encode_dict(packet)
        self.kdc_connection.sendall(packet)

        encrypted_packet = self.kdc_connection.recv(1024)
        encrypted_packet = encrypted_packet.decode('UTF-8')

        des = ToyDES(self.secret_s)
        decrypted_packet = ""
        for byte in encrypted_packet:
            decrypted_packet += chr(des.decrypt(ord(byte)))

        decrypted_packet = json.loads(decrypted_packet)
        self.k_ab = decrypted_packet['k_ab']
        self.k_ab_e = decrypted_packet['k_ab_e']
        self.nonce_b_e = decrypted_packet['nonce_b_e']

    def host_client(self):
        """
        Bob will host Alice's connection
        """
        self.alice_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alice_sock.bind(self.bob_address_2)
        self.alice_sock.listen(1)
        print("Waiting for Alice at", self.bob_address_2)
        self.alice_connection, self.alice_address = self.alice_sock.accept()
        print("Connected to Alice")

        packet = self.alice_connection.recv(1024)
        packet = decode_dict(packet)
        k_ab_e = packet['k_ab_e']
        nonce_b_e = packet['nonce_b_e']
        des = ToyDES(self.secret_s)
        if nonce_b_e == self.replay_nonce:
            print("Replay attack prevented; nonces match!")
        else:
            print("Replay attack possible; nonces do not match!")

        k_ab = des.decrypt(k_ab_e)

        packet = {'type': "ACK"}
        packet = encode_dict(packet)
        self.alice_connection.sendall(packet)

        packet = self.alice_connection.recv(1024)
        packet = packet.decode('UTF-8')

        des.set_key(k_ab)
        decrypted_msg = ""
        for byte in packet:
            decrypted_msg += chr(des.decrypt(ord(byte)))
        print("Recv'd from alice: ", decrypted_msg)

    def join_client(self, msg):
        """
        Alice will connect on Bob's open socket
        """
        self.bob_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bob_sock.connect(self.bob_address_2)

        packet = {'k_ab_e': self.k_ab_e, 'nonce_b_e': self.nonce_b_e}
        packet = encode_dict(packet)
        self.bob_sock.sendall(packet)

        packet = self.bob_sock.recv(1024)
        des = ToyDES(self.k_ab)
        msg_to_send = ""
        for byte in msg:
            encrypted_byte = chr(des.encrypt(ord(byte)))
            msg_to_send += encrypted_byte
        msg_to_send = msg_to_send.encode('UTF-8')
        self.bob_sock.sendall(msg_to_send)

    def send_pg(self):
        """
        Send over p and g to KDC for DH algorithm
        """
        packet = {'type': 'DH_1', 'from': self.user, 'p': self.p, 'g': self.g}
        packet = encode_dict(packet)
        self.kdc_sock.sendall(packet)

    def send_A(self):
        """
        Send over A to KDC for KDC to compute secret_s
        """
        A = (self.g ** self.secret_a) % self.p
        packet = {'type': "DH_2", 'from': self.user, 'A': A}
        packet = encode_dict(packet)
        self.kdc_sock.sendall(packet)

    def recv_B(self):
        """
        Recv B from KDC so client can compute secret_s
        """
        packet = self.kdc_sock.recv(1024)
        packet = decode_dict(packet)
        B = packet['B']
        self.secret_s = (B ** self.secret_a) % self.p

    def send_ack(self):
        """
        Send an ACK packet to KDC
        """
        packet = {'type': "ACK", 'from': self.user}
        packet = encode_dict(packet)
        packet = self.kdc_sock.sendall(packet)

    def recv_ack(self):
        """
        Receives ACK packet; if reply packet was not ACK, then abort
        """
        packet = self.kdc_sock.recv(1024)
        packet = decode_dict(packet)
        if packet['type'] != "ACK":
            print("No ack recv'd!")
            sys.exit()
