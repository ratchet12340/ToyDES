import socket
import sys

from client import Client
from toy_des import ToyDES
from util import parse_secret_key, gen_nonce

if __name__ == "__main__":
    # Parse cmd-line arguments and generate 10-bit key
    if len(sys.argv) != 2:
        print("Correct usage: $ python3 alice.py msg_to_send")
        sys.exit()
    (_, msg_to_send) = sys.argv

    alice = Client(gen_nonce(), gen_nonce(), gen_nonce(), "alice")

    # DH part
    alice.connect_to_KDC()
    alice.send_pg()
    alice.recv_ack()
    alice.close_connection_to_KDC()
    alice.connect_to_KDC()
    alice.send_A()
    alice.recv_B()

    # Prevent replay attacks
    alice.get_nonce_from_bob()

    # NS part
    alice.wait_for_NS()
    alice.start_NS()
    alice.join_client(msg_to_send)
