combos = []

for i in range(16):
    for j in range(16):
        if i ^ j == 3:
            if (j, i) not in combos:
                combos.append((i, j))

print("Values that XOR to 3:", combos)

s0 = [[1, 0, 3, 2], [3, 2, 1, 0], [3, 2, 1, 0], [3, 1, 3, 2]]
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

print(8 ^ 9)
print(8 ^ 10)
