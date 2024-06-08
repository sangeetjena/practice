"""
https://leetcode.com/problems/backspace-string-compare/description/
https://www.youtube.com/watch?v=k2qrymM_DOo
easy way to use two stack and pop elements if encounter "#" but it will take extra space.
"""


class Solution:
    def backspaceCompare(self, s: str, t: str) -> bool:
        def nexIndex(index, st):
            backspace = 0
            while index>=0:
                if backspace == 0 and st[index]!='#':
                    return index
                if st[index]=='#':
                    backspace+=1
                else:
                    backspace-=1
                index-=1
            return index
        i = len(s)
        j = len(t)
        while i>=0 and j>=0:
            i = nexIndex(i-1, s)
            j = nexIndex(j-1,t)
            print(i,j)
            if i<0 and j<0:
                return True
            if i<0 or j<0:
                return False
            if s[i] != t[j]:
                return False
            
        return True 
