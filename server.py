import socket
import sys
from toy_des import ToyDES

if __name__ == "__main__":
    # Parse cmd-line arguments and generate 10-bit key
    if len(sys.argv) != 3:
        print("Correct usage: $ python3 server.py key_num key_letter")
        sys.exit()
    (_, key_num, key_letter) = sys.argv

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

    # Create socket to talk with clients
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind socket to localhost:42010
    hostname = "localhost"
    port_num = 42010
    print("Server started at %s:%d" % (hostname, port_num))
    address = (hostname, port_num)
    sock.bind(address)

    # Handle one request only
    sock.listen(1)

    while True:
        # Blocking call for a connection
        connection, client_address = sock.accept()
        try:
            print('New client:', client_address)

            # Retrieve the filename from the client
            filename = connection.recv(1024)
            filename.decode('ascii')

            # Respond with an ACK acknowledging we have recv'd filename
            ack = b"ACK"
            connection.sendall(ack)

            # Receive file contents
            message = b""
            while True:
                data = connection.recv(1)
                if not data:
                    break
                message += data

            # Decode recv'd bytes back to Unicode
            message = message.decode('UTF-8')
            decrypted_msg = ""

            # Decrypt the recv'd file contents
            for character in message:
                decrypted_msg += chr(toy_des.decrypt(ord(character)))

            # Write the decrypted file contents to disk
            with open(filename, 'w') as f:
                f.write(decrypted_msg)

        # File transfer complete
        finally:
            print("File transfer complete. Closing connection...")
            connection.close()
