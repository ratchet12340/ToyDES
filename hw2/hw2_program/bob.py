import socket
import sys
import time

from util import gen_nonce
from toy_des import ToyDES
from client import Client

if __name__ == "__main__":
        bob = Client(gen_nonce(), gen_nonce(), gen_nonce(), "bob")

        bob.connect_to_KDC()
        bob.send_pg()
        bob.recv_ack()

        bob.connect_to_KDC()
        bob.send_A()
        bob.recv_B()


        bob.host_client()
