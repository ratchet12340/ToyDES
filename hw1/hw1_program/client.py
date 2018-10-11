import socket
import sys
from toy_des import ToyDES

if __name__ == "__main__":
    # Parse cmd-line arguments and generate 10-bit key
    if len(sys.argv) != 5:
        print("correct usage: $ python3 client.py input_file output_file key_num key_letter")
        sys.exit()
    (_, input_file, output_file, key_num, key_letter) = sys.argv

    key_num_domain = [0, 1, 2, 3]

    if int(key_num) not in key_num_domain:
        print("key_num should be 0, 1, 2, or 3")
        sys.exit()

    if len(key_letter) != 1:
        print("key_letter should only be one character")
        sys.exit()

    key = (int(key_num) << 8) | ord(key_letter)

    # Initialize our toy DES object with our formed 10-bit key
    toy_des = ToyDES(key)

    # Create socket to talk with server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the host:port where server is running on
    address = ('localhost', 42010)
    sock.connect(address)

    try:
        # First, send the output filename to the server
        message = output_file.encode('ascii')
        sock.sendall(message)

        # Wait for an ACK acknowledging the output filename
        data = sock.recv(3)
        data = data.decode('ascii')
        if data != "ACK":
            print("Failed to receive an ACK from server! Exiting...")
            sys.exit()

        message = ""
        original = ""

        # Encrypt file and send to server
        with open(input_file) as f:
            one_byte = f.read(1)
            while one_byte != "":
                encrypted_byte = chr(toy_des.encrypt(ord(one_byte)))
                message += encrypted_byte
                one_byte = f.read(1)

        #print('encrypted message is: {!r}'.format(message))
        message = message.encode('UTF-8')
        sock.sendall(message)

    finally:
        print("Sent! Closing connection...")
        sock.close()
