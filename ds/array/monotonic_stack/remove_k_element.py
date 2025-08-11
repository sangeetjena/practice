"""
https://leetcode.com/problems/remove-k-digits/description/

Given string num representing a non-negative integer num, and an integer k, return the smallest possible integer after removing k digits from num.

 

Example 1:

Input: num = "1432219", k = 3
Output: "1219"
Explanation: Remove the three digits 4, 3, and 2 to form the new number 1219 which is the smallest.
Example 2:

Input: num = "10200", k = 1
Output: "200"
Explanation: Remove the leading 1 and the number is 200. Note that the output must not contain leading zeroes.
Example 3:

Input: num = "10", k = 2
Output: "0"
Explanation: Remove all the digits from the number and it is left with nothing which is 0.

Note: monotonic stack problem

"""

class Solution:
    def removeKdigits(self, num: str, k: int) -> str:
        # add base case
        if len(num) == k:
            return "0"
        stack = [int(num[0])]
        cnt = 0
        for i in range(1,len(num)):
            while stack and int(num[i]) < stack[-1] and cnt<k:
                del stack[-1]
                cnt+=1
            stack.append(int(num[i]))
        if cnt < k:
            stack = stack[:len(stack)-(k-cnt)]
        print(stack)
        return str(int("".join([str(x) for x in stack])))



        
