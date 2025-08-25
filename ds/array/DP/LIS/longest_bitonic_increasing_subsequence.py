"""
Given an array arr[] containing n positive integers, a subsequence of numbers is called bitonic if it is first strictly increasing, then strictly decreasing. The task is to find the length of the longest bitonic subsequence. 
Note: Only strictly increasing (no decreasing part) or a strictly decreasing sequence should not be considered as a bitonic sequence.

Input: arr[]= [12, 11, 40, 5, 3, 1]
Output: 5 
Explanation: The Longest Bitonic Subsequence is {12, 40, 5, 3, 1} which is of length 5.

Input: arr[] = [80, 60, 30]
Output: 0
Explanation: There is no possible Bitonic Subsequence.


Note: same as LIS but to find bitonic we need to parse the array from oposite direction and store it to other db,
then add the value at same position in the two dp -1.
"""

# Python implementation to find the longest 
# bitonic subsequence using tabulation 
def LongestBitonicSequence(arr):
    n = len(arr)

    # If there are less than 3 elements,
    # no bitonic subsequence exists
    if n < 3:
        return 0

    # Create lists for longest increasing subsequence
    # (LIS) and longest decreasing subsequence (LDS)
    left = [1] * n
    right = [1] * n

    # Fill left list for LIS
    for i in range(1, n):
        for j in range(i):
            
            # If arr[i] is greater than arr[j],
            # update LIS value at i
            if arr[i] > arr[j]:
                left[i] = max(left[i], left[j] + 1)

    # Fill right list for LDS
    for i in range(n - 2, -1, -1):

        # Compare each element with subsequent
        # ones to build LDS
        for j in range(n - 1, i, -1):

            # If arr[i] is greater than arr[j],
            # update LDS value at i
            if arr[i] > arr[j]:
                right[i] = max(right[i], right[j] + 1)

    # Calculate the maximum length of bitonic subsequence
    maxLength = 0
    for i in range(n):
        
        # Check if both LIS and LDS are valid
        # for the current index
        if left[i] > 1 and right[i] > 1:
            
            # Update maxLength considering both LIS
            # and LDS, subtracting 1 for the peak element
            maxLength = max(maxLength, left[i] + right[i] - 1)

    # If no valid bitonic sequence, return 0
    return maxLength if maxLength >= 3 else 0


if __name__ == "__main__":
    arr = [12, 11, 40, 5, 3, 1]

    print(LongestBitonicSequence(arr))
