"""
https://leetcode.com/problems/minimum-operations-to-reduce-x-to-zero/description/

You are given an integer array nums and an integer x. In one operation, you can either remove the leftmost or the rightmost element from the array nums and subtract its value from x. Note that this modifies the array for future operations.

Return the minimum number of operations to reduce x to exactly 0 if it is possible, otherwise, return -1.

 

Example 1:

Input: nums = [1,1,4,2,3], x = 5
Output: 2
Explanation: The optimal solution is to remove the last two elements to reduce x to zero.
Example 2:

Input: nums = [5,6,7,8,9], x = 4
Output: -1
Example 3:

Input: nums = [3,2,20,1,1,3], x = 10
Output: 5
Explanation: The optimal solution is to remove the last three elements and the first two elements (5 operations in total) to reduce x to zero.

Note:
insteed of finding side two window find midle window which value should be sum(nums) - x


"""
class Solution:
    def minOperations(self, nums: List[int], x: int) -> int:
        sm = sum(nums)
        if sm< x:
            return -1
        if sm == x:
            return len(nums)
        target = sm-x
        temp_sm = 0
        mx_op = -1
        s=0
        e=0
        print(sm,target, x)
        while e< len(nums):
            temp_sm+=nums[e]
            while temp_sm >= target and target!=0:
                if temp_sm==target:
                    mx_op = max(mx_op, e-s+1)
                temp_sm-=nums[s]
                s+=1
            e+=1
        return mx_op if mx_op==-1 else len(nums)-mx_op


                
        
