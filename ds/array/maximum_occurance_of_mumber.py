"""
The frequency of an element is the number of times it occurs in an array.

You are given an integer array nums and an integer k. In one operation, you can choose an index of nums and increment the element at that index by 1.

Return the maximum possible frequency of an element after performing at most k operations.



Example 1:

Input: nums = [1,2,4], k = 5
Output: 3
Explanation: Increment the first element three times and the second element two times to make nums = [4,4,4].
4 has a frequency of 3.
"""

def max_element(arr, k):
    arr = sorted(arr)
    max_cnt = 0
    for i in range(len(arr)):
        for j in range(len(arr)-i):
            right = j+i
            sm = sum(arr[j:right])
            total = arr[right]*i
            print(arr[j:right])
            print(sm, total)
            if sm + k >= total:
                max_cnt = i
                break
    return max_cnt

# arr = [1,2,4]
# print(max_element(arr,5))

arr = [1,4,8,13]
print(max_element(arr,5))
