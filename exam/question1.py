def hash_func(x):
    hash_val = 0
    for i,c in enumerate(x):
        if i == 0:
            continue

        if i % 3 == 0:
            hash_val = hash_val + ord(c)
    return hash_val

if __name__ == "__main__":
    msg1 = "meet5pm!"
    msg2 = "dontcome"
    print("Intended message:", msg1)
    print("Message created for collision attack:", msg2)
    print("Hash of intended message:", hash_func(msg1))
    print("Hash of attack message:", hash_func(msg2))
