import socket
import sys
import time

from util import gen_nonce
from toy_des import ToyDES
from client import Client

if __name__ == "__main__":
        bob = Client(gen_nonce(), gen_nonce(), gen_nonce(), "bob")

        # DH part
        bob.connect_to_KDC()
        bob.send_pg()
        bob.recv_ack()

        bob.connect_to_KDC()
        bob.send_A()
        bob.recv_B()

        # Replay part
        bob.send_nonce_to_alice()

        # NS part
        bob.host_client()
