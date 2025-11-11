"""
https://www.geeksforgeeks.org/dsa/find-the-missing-number-in-a-sorted-array/

Note:
approach 1: search index position = num -1 (O(n))
approach 2: search next value should be val(i) - val(i+1) = 1
approach 3: sum of all value of all natural number of n -> (n*n-1)/2,,  add all value in array. now missing element = n*(n-1)/2 - sum(array)  , this is O(n)
approach 4: binary search , n/2 to n index positon should have (n/2-n +1) element, else there is a missing element. -> O(logn)

"""

# O(n)

def missingNumber(arr):
  
    # Calculate the total sum
    n = len(arr) + 1
    totalSum = n * (n + 1) // 2

    # Calculate sum of all elements in the given list
    arraySum = sum(arr)

    # Subtract and return the missing number
    missingNumber = totalSum - arraySum

    return missingNumber

if __name__ == "__main__":
    arr = [1, 2, 3, 4, 6, 7, 8]
    print(missingNumber(arr))

# Binary search

def missingNumber(arr):
    n = len(arr)
    
    # Extreme cases
    if arr[0] != 1:
        return 1
    if arr[n - 1] != n + 1:
        return n + 1
        
    # Implementing binary search
    lo, hi = 0, n - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if arr[lo] - lo != arr[mid] - mid:
            hi = mid
        elif arr[hi] - hi != arr[mid] - mid:
            lo = mid
    return arr[lo] + 1

if __name__ == "__main__":
    arr = [1, 2, 3, 4, 6, 7, 8]
    print(missingNumber(arr))
