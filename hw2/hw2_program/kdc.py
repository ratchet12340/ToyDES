import socket
import sys
import random
import json

from toy_des import ToyDES
from util import encode_dict, decode_dict, gen_nonce

"""
DH_dict =
{
    alice: {
        connection: ?,
        p: ?,
        g: ?,
        secret_b: ?,
        secret_s: ?
    },
    bob: {
        connection: ?,
        p: ?,
        g: ?,
        secret_b: ?,
        secret_s: ?
    }
}
"""

class KDC:
    def __init__(self):
        self.kdc_address_1 = ('localhost', 42011)
        self.kdc_address_2 = ('localhost', 42009)
        self.alice_address = ('localhost', 42010)
        self.bob_address = ('localhost', 42012)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("KDC server started at", self.kdc_address_1)
        self.sock.bind(self.kdc_address_1)
        self.sock.listen(1)

        self.dh_dict = {'alice': {}, 'bob': {}}

        self.dh_dict['alice']['secret_b'] = 3
        self.dh_dict['bob']['secret_b'] = 3
        # self.secret_keys = {}

    def recv_pg(self, packet):
        cur_dict = None
        if packet['from'] == "alice":
            cur_dict = self.dh_dict['alice']
        elif packet['from'] == "bob":
            cur_dict = self.dh_dict['bob']

        cur_dict['p'] = packet['p']
        cur_dict['g'] = packet['g']

    def recv_A(self, packet):
        """
        Recv A from client so KDC can compute secret_s
        """
        cur_dict = None
        if packet['from'] == "alice":
            cur_dict = self.dh_dict['alice']
        elif packet['from'] == "bob":
            cur_dict = self.dh_dict['bob']

        A = packet['A']
        secret_b = cur_dict['secret_b']
        p = cur_dict['p']
        cur_dict['secret_s'] = (A ** secret_b) % p

    def send_B(self, connection):
        g = None
        p = None
        secret_b = None
        if connection == self.dh_dict['alice']['connection']:
            g = self.dh_dict['alice']['g']
            p = self.dh_dict['alice']['p']
            secret_b = self.dh_dict['alice']['secret_b']
        elif connection == self.dh_dict['bob']['connection']:
            g = self.dh_dict['bob']['g']
            p = self.dh_dict['bob']['p']
            secret_b = self.dh_dict['bob']['secret_b']
        else:
            print("UH OH")

        B = (g ** secret_b) % p
        packet = {'B': B}
        packet = encode_dict(packet)
        connection.sendall(packet)

    def send_ack(self, connection):
        """
        Send an ACK packet to client
        """
        packet = {'type': "ACK"}
        packet = encode_dict(packet)
        bytes_sent = connection.send(packet)

    def decode_packet(self, packet, connection):
        if packet['from'] == "alice":
            self.dh_dict['alice']['connection'] = connection
        elif packet['from'] == "bob":
            self.dh_dict['bob']['connection'] = connection

        if packet['type'] == "DH_1":
            self.recv_pg(packet)
            self.send_ack(connection)
        elif packet['type'] == "DH_2":
            self.recv_A(packet)
            self.send_B(connection)

    def handle_NS(self):
        packet = self.sock.recv(1024)
        packet = decode_dict(packet)
        nonce_a = packet['nonce_a']

        k_as = self.dh_dict['alice']['secret_s']
        k_bs = self.dh_dict['bob']['secret_s']
        k_ab = random.getrandbits(8)

        des = ToyDES(k_bs)
        k_ab_e = des.encrypt(k_ab)
        packet = {'nonce_a': nonce_a, 'k_ab': k_ab, 'k_ab_e': k_ab_e}
        packet = json.dumps(packet)
        #packet = encode_dict(packet)
        des.set_key(k_as)
        encrypted_packet = ""
        for byte in packet:
            encrypted_byte = chr(des.encrypt(ord(byte)))
            encrypted_packet += encrypted_byte

        encrypted_packet = encrypted_packet.encode('UTF-8')

        self.sock.sendall(encrypted_packet)
        
    def accept_cli(self):
        """
        Accepts new incoming client connections
        """
        while True:
            # Blocking call for a connection
            connection, client_address = self.sock.accept()
            try:
                print('Incoming client:', client_address)
                print('Connection:', connection)

                packet = connection.recv(1024)
                packet = decode_dict(packet)
                self.decode_packet(packet, connection)

                # Check if DH done, move on to NS part
                alice_done = 'secret_s' in self.dh_dict['alice']
                bob_done = 'secret_s' in self.dh_dict['bob']
                if alice_done and bob_done:
                    # Tell alice to begin NS with bob
                    self.sock.close()
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.bind(self.kdc_address_2)
                    self.sock.connect(self.alice_address)
                    self.handle_NS()
                    break

            finally:
                print("Closing connection...")
                connection.close()

if __name__ == "__main__":
    # # Parse cmd-line arguments and generate 10-bit key
    # if len(sys.argv) != 3:
    #     print("Correct usage: $ python3 server.py key_num key_letter")
    #     sys.exit()
    # (_, key_num, key_letter) = sys.argv
    #
    # key_num_domain = [0, 1, 2, 3]
    #
    # if int(key_num) not in key_num_domain:
    #     print("key_num should be 0, 1, 2, or 3")
    #     sys.exit()
    #
    # if len(key_letter) != 1:
    #     print("key_letter should only be one character")
    #     sys.exit()
    #
    # key = (int(key_num) << 8) | ord(key_letter)
    #
    # # Initialize our toy DES object with our formed 10-bit key
    # toy_des = ToyDES(key)

    kdc = KDC()
    kdc.accept_cli()

    #         # Respond with an ACK acknowledging we have recv'd filename
    #         ack = b"ACK"
    #         connection.sendall(ack)
    #
    #         # Receive file contents
    #         message = b""
    #         while True:
    #             data = connection.recv(1)
    #             if not data:
    #                 break
    #             message += data
    #
    #         # Decode recv'd bytes back to Unicode
    #         message = message.decode('UTF-8')
    #         decrypted_msg = ""
    #
    #         # Decrypt the recv'd file contents
    #         for character in message:
    #             decrypted_msg += chr(toy_des.decrypt(ord(character)))
    #
    #         # Write the decrypted file contents to disk
    #         with open(filename, 'w') as f:
    #             f.write(decrypted_msg)
    #
        # File transfer complete
