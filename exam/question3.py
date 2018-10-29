import sys
import random

def compute_gcd(x, y):
    """
    For use with Pollard-Rho
    """
    while(y):
        x, y = y, x % y
    return x

def gx(x, n):
    return (x * x + 1) % n

def pollard_rho(n):
    """
    Find factors of a number with Pollard-Rho algorithm.
    """
    number = 10403
    cycle_size = 2
    x = 2
    y = 2
    d = 1

    for i in range(100):
        x = gx(x, n)
        y = gx(gx(y, n), n)
        d = compute_gcd(abs(y - x), n)

        print("factor is:", d)

def test_base(a, n, s, d):
    """
    For use with Miller-Rabin
    """
    if pow(a, d) % n == 1:
        return False
    for i in range(s):
        if pow(a, pow(2, i) * d) % n == n - 1:
            return False
    return True

def random_base_test(n, s ,d):
    """
    For use with Miller-Rabin
    """
    for i in range(25):
        a = random.randrange(2, n)
        if test_base(a, n, s, d):
            return False
    return True

def miller_rabin(n):
    """
    Miller-Rabin Algorithm to determine whether n is prime.
    """
    base_composites = [0, 1, 4, 6, 8, 9]
    base_primes = [2, 3, 5, 7]

    if n in base_composites:
        return False
    if n in base_primes:
        return True

    s = 0
    d = n - 1
    while d % 2 == 0:
        # Multiplying by 2 slows performance drastically
        d = d >> 1
        s = s + 1

    # Choose random bases since we do not know dist. of witnesses
    result = random_base_test(n, s, d)

    return result

if __name__ == "__main__":
    num_to_test = int(sys.argv[1])
    is_prime = miller_rabin(num_to_test)
    print(num_to_test, "is prime:", is_prime)

    # Composite number; find factors with Pollard-Rho
    if is_prime == False:
        pollard_rho(num_to_test)
