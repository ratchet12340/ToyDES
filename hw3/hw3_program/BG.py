if __name__ == "__main__":
    # set up variables
    p = 499
    q = 547
    a = -57
    b = 52
    n = p * q
    h = 4
    k = 18
    x_0 = 159201

    plaintext = '10011100000100001100'
    print("Original plaintext:", plaintext)

    plaintext_len = len(plaintext)
    plaintext = int(plaintext, 2)

    num_blocks = int(plaintext_len/h)
    x_i = x_0
    encrypted = 0

    # encryption
    for i in range(num_blocks - 1 , -1, -1):
        h_bits = 1 << h
        h_bits = h_bits - 1
        x_i = pow(x_i, 2, n)
        number = plaintext >> (h * i)
        m_i = number & h_bits
        p_i = x_i & h_bits
        c_i = p_i ^ m_i
        encrypted = (encrypted << h) | c_i
    x_i = pow(x_i, 2, n)

    # now have ciphertext
    print("Ciphertext: (%s, %d)" % (bin(encrypted), x_i))

    # decryption
    r_p = pow(int((p + 1) / 4), 6, p - 1)
    r_q = pow(int((q + 1) / 4), 6, q - 1)
    u = pow(x_i, r_p, p)
    v = pow(x_i, r_q, q)
    l = v * a * p
    r = u * b * q
    x_0 = (l + r) % n
    decrypted = 0
    x_i = x_0
    for i in range(4, -1, -1):
        h_bits = 1 << h
        h_bits = h_bits - 1
        x_i = pow(x_i, 2, n)
        selector = encrypted >> (h * i)
        c_i = selector & h_bits
        p_i = x_i & h_bits
        m_i = p_i ^ c_i
        decrypted = (decrypted << h) | m_i

    # decryption done
    print("Decrypted plaintext:", bin(decrypted))
