import sys

def find_min_coin(coins, total):
    sums = [sys.maxsize for x in range(total + 1)]
    sums[0] = 0
    # index represent sum
    for i in range(1,total +1):
        for j in coins:
            if(j<= i and sums[i-j] != sys.maxsize):
                sums[i] = min(sums[i], 1 + sums[i-j])
    print(sums)
    return sums[-1]

print(find_min_coin([3,5,7], 17))