"""
https://leetcode.com/problems/generate-parentheses/
back tracking
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
            if cb < ob:
                if ob < n:
                    findParanth(par + "(", ob+1, cb)
                if cb <n:
                    findParanth(par+")", ob, cb+1)
            else:
                if ob < n:
                    findParanth(par + "(", ob+1, cb)
        findParanth(par,ob,cb)
        print(finallist)
        return finallist
