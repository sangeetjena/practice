"""
https://leetcode.com/problems/next-greater-element-iii/description/?envType=problem-list-v2&envId=two-pointers

Given a positive integer n, find the smallest integer which has exactly the same digits existing in the integer n and is greater in value than n. If no such positive integer exists, return -1.

Note that the returned integer should fit in 32-bit integer, if there is a valid answer but it does not fit in 32-bit integer, return -1.

Example 1:

Input: n = 12
Output: 21
Example 2:

Input: n = 21
Output: -1

Constraints:

1 <= n <= 231 - 1

"""

class Solution:
    def nextGreaterElement(self, n: int) -> int:
        stack = []
        elem = []
        k,l = 0,0
        replace = 0
        while n>0:
            elem.append(n%10)
            n = n //10
        for i in range(len(elem)):
            # in monotonic stack pattern find 1st index from lower decimal place can be swapable
            while len(stack) > 0 and elem[i]< stack[-1][0]:
                k,l = i, stack[-1][1]
                stack.pop()
                replace = 1
            if replace == 1:
                elem[k], elem[l] = elem[l], elem[k]
                print(elem, k,l)
                # after swaping the smallest bigger elemt in the ith position rest of the element in the lower decimal place can simply sorted in asc order to get the smallest greater number 
                #ex: 230241
                # 230421 ( index 2,3) but after swaping if we will sort after 2nd index we will still get elemt which is greater than current elem.
                # ans: 230412
                ret = int("".join(str(x) for x in reversed(sorted(elem[:i], reverse=True) + elem[i:])))
                # Note: if after swap check if elem is corssing number range or not.
                return ret if ret <= 2**31 - 1 else -1
            stack.append((elem[i],i))
        return -1
            
