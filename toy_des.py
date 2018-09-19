# Constants used in the DES algorithm (permutation tables and S-Boxes)
p10 = (3, 5, 2, 7, 4, 10, 1, 9, 8, 6)
p8 = (6, 3, 7, 4, 8, 5, 10, 9)
p4 = (2, 4, 3, 1)
ip = (2, 6, 3, 1, 4, 8, 5, 7)
e_table = (4, 1, 2, 3, 2, 3, 4, 1)
inverse_ip = (4, 1, 3, 5, 7, 2, 8, 6)
sbox_0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
sbox_1 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]

class ToyDES:
    """
    The ToyDES class implements the toy DES encryption algorithm as specified
    in the lecture slides.
    It is easy to use:
    First, initialize this class with a 10-bit key.
    Next, encrypt/decrypt a byte with the encrypt/decrypt functions.
    """

    def __init__(self, key):
        """
        When initializing ToyDES, a key must be provided to generate subkeys.
        This key is a 10 bit number
        """
        (k1, k2) = self.generate_keys(key)
        self.k1 = k1
        self.k2 = k2

    def generate_keys(self, initial_key):
        """
        Generates the subkeys k1 and k2 based on the initial key specified.
        Initial key must be 10 bits in size.
        """
        # Perform P10 permutation on initial key
        p10_key = self.permute(initial_key, p10)

        # Now we must split the permuted key into two 5-bit halves
        (p10_left_base, p10_right_base) = self.split_bits(p10_key, 5)

        # Now we do the special left shift process on each half to generate K1 and K2
        p10_left_1 = self.left_shift(p10_left_base)
        p10_right_1 = self.left_shift(p10_right_base)

        # Re-combine the two halves
        k1 = (p10_left_1 << 5) | p10_right_1

        # Do P8 permutation table on first subkey for final first subkey
        k1 = self.permute(k1, p8)

        # Do special left shift on previous halves to obtain subkey #2
        p10_left_2 = self.left_shift(p10_left_1)
        p10_right_2 = self.left_shift(p10_right_1)
        k2 = (p10_left_2 << 5) | p10_right_2
        k2 = self.permute(k2, p8)

        return (k1, k2)

    def left_shift(self, one_half):
        """
        The 'special left shift' function that will shift bits to the left while
        cycling the last bit back to the beginning of the 5 bits.
        Used with generating keys (hence why code below assumes one_half is 5 bits)
        """
        fifth_bit_selector = 0b10000
        fifth_bit = (one_half & fifth_bit_selector) >> 4
        four_bit_selector = 0b01111
        four_bits = one_half & four_bit_selector
        result = (four_bits << 1) | fifth_bit
        return result

    def permute(self, key, table):
        """
        Permutes the provided key via the provided permute table.
        Each permutation table index indexes the key from the right to left.
        The final permuted key is built from right to left.
        """
        table_len = 0
        permuted_key = 0

        for index in table:
            # First, grab the bit specified by the permutation table
            bit_selector = 1 << index - 1
            selected_bit = key & bit_selector

            # Next, we shift the selected bit back to the right to get a plain 1 or 0
            selected_bit = selected_bit >> index - 1

            # Finally, append the selected bit to the end of our permuted key
            permuted_key = permuted_key | (selected_bit << table_len)
            table_len += 1

        return permuted_key

    def split_bits(self, bits, half_size):
        """
        Split provided bits into left and right half_size sized halves.
        """
        bit_selector = 1
        for i in range(half_size-1):
            bit_selector = (bit_selector << 1) | 1
        left = bit_selector & (bits >> half_size)
        right = bit_selector & bits
        return (left, right)

    def sbox(self, input_bits, matrix):
        """
        Run the sbox specified by matrix on specified input_bits
        """
        first_bit = input_bits & 0b0001
        second_bit = (input_bits & 0b0010) >> 1
        third_bit = (input_bits & 0b0100) >> 2
        fourth_bit = (input_bits & 0b1000) >> 3
        # bit2 and bit3
        column_bits = (third_bit << 1) | second_bit
        # bit1 and bit4
        row_bits = (fourth_bit << 1) | first_bit
        return matrix[row_bits][column_bits]

    def round_func(self, right_input, subkey):
        """
        This is the function f used in each round of DES.
        """
        # First step of f(R_n-1, K_n) is to expand R_n-1
        expanded_right = self.permute(right_input, e_table)

        # Next step is to XOR expanded 8-bit right half with 8-bit key
        xor_result = expanded_right ^ subkey

        # Split the 8-bit XOR result into two 4-bit halves
        (left, right) = self.split_bits(xor_result, 4)

        # Next, use s-boxes to shrink the 4-bit xor result halves to 2 bits each
        sbox_result_0 = self.sbox(left, sbox_0)
        sbox_result_1 = self.sbox(right, sbox_1)
        sbox_result = (sbox_result_0 << 2) | sbox_result_1

        # Do a final permutation with P4 and return
        return self.permute(sbox_result, p4)

    def encrypt(self, byte_to_encrypt):
        """
        Use Toy DES encryption algorithm to encrypt provided byte.
        """
        #input_block = int.from_bytes(byte_to_encrypt.encode(), byteorder='big')
        input_block = byte_to_encrypt

        # First, permute the input
        permuted_input = self.permute(input_block, ip)

        # Next, divide into two 4-bit halves
        (left_input_base, right_input_base) = self.split_bits(permuted_input, 4)

        # Round 1 of DES
        left_input_1 = right_input_base
        right_input_1 = left_input_base ^ self.round_func(right_input_base, self.k1)

        # Round 2 of DES
        left_input_2 = right_input_1
        right_input_2 = left_input_1 ^ self.round_func(right_input_1, self.k2)

        # Do a final reverse and combine left and right into 8 bits of ciphertext
        ciphertext = (right_input_2 << 4) | left_input_2

        # Apply inverse of IP to ciphertext for final result
        ciphertext = self.permute(ciphertext, inverse_ip)
        return ciphertext

    def decrypt(self, byte_to_decrypt):
        """
        Use Toy DES encryption algorithm in reverse to decrypt the ciphertext
        """
        #ciphertext = int.from_bytes(byte_to_decrypt.encode(), byteorder='big')
        ciphertext = byte_to_decrypt

        # Undo inverse of IP to ciphertext
        ciphertext = self.permute(ciphertext, ip)

        # Un-reverse the final reverse and split
        right_input_2 = (ciphertext & 0b11110000) >> 4
        left_input_2 = ciphertext & 0b1111

        # Undo round 2 of original DES algorithm
        right_input_1 = left_input_2
        left_input_1 = right_input_2 ^ self.round_func(left_input_2, self.k2)

        # Undo round 1 of original DES algorithm
        right_input_base = left_input_1
        left_input_base = right_input_1 ^ self.round_func(left_input_1, self.k1)

        # Combine the decrypted input bases and undo initial permutation
        permuted_base = (left_input_base << 4) | right_input_base
        unpermuted_base = self.permute(permuted_base, inverse_ip)
        return unpermuted_base
