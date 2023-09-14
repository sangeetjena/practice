import sys


def nap_sack(coins, total):
    bag = [sys.maxsize for i in range(total + 1)]
    bag[0] = 0
    for i in range(1, total + 1):
        for j in coins:
            if j <= i and bag[i-j] != sys.maxsize and i-j != j:
                print(i, j)
                print(bag[i], 1 + bag[i - j])
                bag[i] = min(bag[i], 1+bag[i-j])
    print(bag)
    if bag[-1] == sys.maxsize:
        return "not possible"
    else:
        return bag[-1]

print(nap_sack([2,5,7], 15))