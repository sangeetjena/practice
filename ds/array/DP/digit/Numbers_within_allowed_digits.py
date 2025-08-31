"""
https://leetcode.com/problems/numbers-at-most-n-given-digit-set/description/

Given an array of digits which is sorted in non-decreasing order. You can write numbers using each digits[i] as many times as we want. For example, if digits = ['1','3','5'], we may write numbers such as '13', '551', and '1351315'.

Return the number of positive integers that can be generated that are less than or equal to a given integer n.

 

Example 1:

Input: digits = ["1","3","5","7"], n = 100
Output: 20
Explanation: 
The 20 numbers that can be written are:
1, 3, 5, 7, 11, 13, 15, 17, 31, 33, 35, 37, 51, 53, 55, 57, 71, 73, 75, 77.
Example 2:

Input: digits = ["1","4","9"], n = 1000000000
Output: 29523
Explanation: 
We can write 3 one digit numbers, 9 two digit numbers, 27 three digit numbers,
81 four digit numbers, 243 five digit numbers, 729 six digit numbers,
2187 seven digit numbers, 6561 eight digit numbers, and 19683 nine digit numbers.
In total, this is 29523 integers that can be written using the digits array.
Example 3:

Input: digits = ["7"], n = 8
Output: 1


Note: same as numbers of one, only difference is insteed of taking any number from 0 to 9 , fixed set of intergers has given in an array.

"""


from functools import lru_cache

class Solution:
    def atMostNGivenDigitSet(self, digits: List[str], n: int) -> int:
        num = str(n)

        @lru_cache(None)
        def dp(i: int, tight: bool) -> int:
            if i == len(num):
                return 1  # valid number formed

            ans = 0
            limit = int(num[i]) if tight else 9
            for d in digits:
                dval = int(d)
                if dval > limit:
                    break
                new_tight = tight and (dval == limit)
                ans += dp(i + 1, new_tight)
            return ans

        # Count numbers with length < len(num)
        total = 0
        m = len(digits)
        for k in range(1, len(num)):
            total += m ** k

        # Count numbers with same length as num using DP
        total += dp(0, True)
        return total
