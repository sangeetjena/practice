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

"""
class Solution:
    def nextGreaterElement(self, n: int) -> int:
        # to find the closest greater element, we need to look from left to write of a number
        # and swap a number in higher index position with a number in the lower index position which is greater than present value and sort rest of the elemnet position from lower to hightest.
        # ex: 14[2]321 -> 14[3]122
        s = [str(n)[i] for i in range(len(str(n)))]
        print(s)
        ind = -1
        # find the index position where we can replace the value to get the greater element.
        for i in reversed(range(1,len(s))):
            if s[i-1]<s[i]:
                ind=i-1
                break
        if ind==-1:
            return -1
         # note don't just replace when find num[i-1] < num[i] , find then smallest element greter than num[i-1]
        for j in reversed(range(ind,len(s))):
            if s[j]>s[ind]:
                s[j],s[ind] = s[ind], s[j]
                break
        s = s[:ind+1] + sorted(s[ind+1:])
        x = int("".join(s))
        return x if x < 2**31 else -1

        
