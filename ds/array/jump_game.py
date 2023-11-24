"""
Given an array of integers where each element represents the max number of steps that can be made forward from that element. Write a function to return the minimum number of jumps to reach the end of the array (starting from the first element). If an element is 0, then we cannot move through that element. If we can’t reach the end, return -1.

Input: arr[] = {1, 3, 5, 8, 9, 2, 6, 7, 6, 8, 9}
Output: 3 (1-> 3 -> 8 -> 9)
Explanation: Jump from 1st element to 2nd element as there is only 1 step, now there are three options 5, 8 or 9. If 8 or 9 is chosen then the end node 9 can be reached. So 3 jumps are made.

Input : arr[] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1}
Output: 10
Explanation: In every step a jump is needed so the count of jumps is 10.
"""

def jump_game(arr, i,distance, dest, cnt):
    if i+distance >= dest:
        return cnt
    mincnt = 99999999
    for i in range(i+1, i+1+distance):
        mincnt = min( mincnt, jump_game(arr, i, arr[i], dest, cnt+1))
    return mincnt

arr = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

print(jump_game(arr, 0, arr[0], 9, 0))

arr = [1, 3, 4, 5, 1, 1, 1, 7, 2, 1, 9]
print(jump_game(arr, 0, arr[0], 11, 0))
