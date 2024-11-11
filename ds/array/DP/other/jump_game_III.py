"""
https://leetcode.com/problems/jump-game-iii/

Given an array of non-negative integers arr, you are initially positioned at start index of the array. When you are at index i, you can jump to i + arr[i] or i - arr[i], check if you can reach any index with value 0.

Notice that you can not jump outside of the array at any time.

 

Example 1:

Input: arr = [4,2,3,0,3,1,2], start = 5
Output: true
Explanation: 
All possible ways to reach at index 3 with value 0 are: 
index 5 -> index 4 -> index 1 -> index 3 
index 5 -> index 6 -> index 4 -> index 1 -> index 3 

Note: dfs, insteed of using visited which is taking some time and causing time limit exceed exception, used same array and replace value to -1 (indicating visited )
"""
class Solution:
    def canReach(self, arr: List[int], start: int) -> bool:
        dfs = []
        dfs.append((start,arr[start]))
        while dfs:
            i, w  = dfs[-1]
            if arr[i] == -1:
                del dfs[-1]
                continue
            if arr[i] == 0:
                return True
            arr[i] = -1
            # check two position if not in visited then add in dfs
            if 0<=i+w<=len(arr)-1 and arr[i+w] != -1 :
                dfs.append((i+w,arr[i+w]))
            if 0<=i-w<=len(arr)-1 and arr[i-w] != -1 :
                dfs.append((i-w,arr[i-w]))
        return False
            
        
