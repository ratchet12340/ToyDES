# ToyDES
Toy DES implementation for CSCI-4230. In short, this program has a client and server that can be ran to send a file "securely" from client to server. The file contents that are sent over the wire are encrypted with the ToyDES encryption algorithm.

# Getting Started
To get this program up and running on your machine, you will need Python 3+ installed. Once you have that, follow these steps:
1. Clone this repository.
2. `cd` into your cloned repo.
3. Run the server with `python3 server.py key_num key_char` (more on key_num / key_char in next section)
4. Run the client with `python3 client.py input_file output_file key_num key_char` (more on these parameters in the next two sections)
5. Done! You should have successfully transferred a file from client to server and encrypted the file contents that were sent over the wire.

# How does the key work?
Since the key is specified to be 10-bits wide, you can provide a number within the range 0-3 for the first 2 bits, then a character of your choosing for the remaining 8 bits. So, for example, on the command line you provide `3` for `key_num` and `G` for `key_char` then the resulting key will take the form: `0b11` + `0b01000111` = `0b1101000111`.

This method was chosen to allow the user to have full control over all 10 bits of the key.

# How does the file transfer work?
An input file is specified by the client program via `input_file`. The contents of this file are the file contents that are sent over to the server. The `output_file` argument specifies the file for the server to write to.

Note, the file contents are encrypted, but the filename is not.

For encryption/decryption to be successful, the key specified by client and server must be the same.
