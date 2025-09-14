"""
https://leetcode.com/problems/generate-parentheses/
Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses.

 

Example 1:

Input: n = 3
Output: ["((()))","(()())","(())()","()(())","()()()"]
Example 2:

Input: n = 1
Output: ["()"]


Note: back tracking take all possbible combination
"""

class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        finallist = []
        par = ""
        ob =cb =0
        def findParanth(par, ob, cb):
            if ob >n or cb >n:
                return
            if len(par) == n*2:
                finallist.append(par)
            # this condition is to ensure always push opening braces before closing braces.
            if cb < ob:
                # if opening braces has pushed more then we have two opetoin open. we can use ob or cb.
                if ob < n:
                    findParanth(par + "(", ob+1, cb)
                if cb <n:
                    findParanth(par+")", ob, cb+1)
            else:
                # if ob are less then we have only one option to take ob only.
                if ob < n:
                    findParanth(par + "(", ob+1, cb)
        findParanth(par,ob,cb)
        print(finallist)
        return finallist

            
                

            
        
