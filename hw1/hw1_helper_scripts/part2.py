s0 = [[1, 0, 3, 2], [3, 2, 1, 0], [3, 2, 1, 0], [3, 1, 3, 2]]

combos = []
combos.append((0b1111, 0b0))
combos.append((0b1010, 0b101))
combos.append((0b1100, 0b11))
combos.append((0b1001, 0b110))
combos.append((0b1110, 0b1))
combos.append((0b111, 0b1000))
combos.append((0b10, 0b1101))
combos.append((0b0100, 0b1011))

for combo in combos:
    result = []
    for input_bits in combo:
        first_bit = input_bits & 0b0001
        second_bit = (input_bits & 0b0010) >> 1
        third_bit = (input_bits & 0b0100) >> 2
        fourth_bit = (input_bits & 0b1000) >> 3

        # bit2 and bit3
        column_bits = (third_bit << 1) | second_bit
        # bit1 and bit4
        row_bits = (fourth_bit << 1) | first_bit

        result.append(s0[row_bits][column_bits])
    print(combo, "XORS to", result[0] ^ result[1], "(",result,")")
