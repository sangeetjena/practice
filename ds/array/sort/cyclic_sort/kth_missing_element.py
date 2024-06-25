"""
https://leetcode.com/problems/kth-missing-positive-number/submissions/1299416779/
"""

class Solution:
    def findKthPositive(self, arr: List[int], k: int) -> int:
        i=-1
        j=0
        p = 0
        while i < len(arr) and j < len(arr) and k>0:
            if arr[j] - p == 1:
                j+=1
                i+=1
                p = arr[i]
                continue
            p+=1
            k-=1
        return p+k
            
            

            
        
