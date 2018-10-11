inlist = [9, 6]
other = [15, 0, 10, 5, 12, 3, 14, 1, 7, 8, 2, 13]

for num1 in inlist:
    for num2 in other:
        print(num1,"XOR",num2,"=",num1^num2)
    print()
