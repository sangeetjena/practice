"""
https://leetcode.com/problems/number-of-digit-one/description/


Given an integer n, count the total number of digit 1 appearing in all non-negative integers less than or equal to n.

 

Example 1:

Input: n = 13
Output: 6
Example 2:

Input: n = 0
Output: 0



Note: digits on dp rule:
1 - move from left to right 
2- we are free to select all the mumber (0-9) if we select the digit other than the last digit for subsequent index position
3- if we select last digit then movement is restricted for its next index, it can move max to the digit value in the next index potition.
"""

class Solution:
    def countDigitOne(self, n: int) -> int:
        nums = str(n)
        @cache
        def dp(i, tight, cnt):
            if i == len(nums):
                return cnt
            # if call has made from the last digit of the previous index then selection is restricted to the value present at that index
            upper = int(nums[i]) if tight else 9
            ans = temp = 0

            for d in range(upper + 1):
                # set the tight flag for last index, as if we will slect the last index it s next index position has restited movement to select the digit. next index position can't select any digit.
                new_tight = tight and d == int(nums[i])
                # increment the count value if the searching digit found.
                if d == 1:
                    temp = 1
                ans += dp(i + 1, new_tight, cnt + temp)
                temp = 0
                
            return ans

        return dp(0, True, 0)
