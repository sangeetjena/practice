"""
https://leetcode.com/problems/letter-case-permutation/

Given a string s, you can transform every letter individually to be lowercase or uppercase to create another string.

Return a list of all possible strings we could create. Return the output in any order.

 

Example 1:

Input: s = "a1b2"
Output: ["a1b2","a1B2","A1b2","A1B2"]
Example 2:

Input: s = "3z4"
Output: ["3z4","3Z4"]

# back tracking
"""


class Solution(object):
    def letterCasePermutation(self, S):
        """
        :type S: str
        :rtype: List[str]
        """
        def backtrack(sub="", i=0):
            if len(sub) == len(S):
                res.append(sub)
            else:
                # if it is alphabet swap once and then take wtihout swap value
                # for numeric only take without swap case 
                if S[i].isalpha():
                    backtrack(sub + S[i].swapcase(), i + 1)
                backtrack(sub + S[i], i + 1)
                
        res = []
        backtrack()
        return res
        
"""
class Solution:
    def letterCasePermutation(self, s: str) -> List[str]:
        # back tracking, similar to subset 1 and 2 problem.
        finallist = []
        lst = s
        ind = -1
        def letterCase(lst, ind):
            if ind > len(s):
                return
            if lst not in finallist:
                finallist.append(lst)
            ind+=1
            temp = ""
            for i in range(len(s)):
                if i == ind:
                    if lst[i].upper() == lst[i]:
                        temp+=lst[i].lower()
                    else:
                        temp+=lst[i].upper()
                else:
                    temp+=lst[i]
            letterCase(lst, ind)
            letterCase(temp, ind)
        letterCase(lst, ind)
        print(finallist)
        return finallist
"""     
