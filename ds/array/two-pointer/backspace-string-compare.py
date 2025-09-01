"""
https://leetcode.com/problems/backspace-string-compare/description/
Given two strings s and t, return true if they are equal when both are typed into empty text editors. '#' means a backspace character.

Note that after backspacing an empty text, the text will continue empty.

 

Example 1:

Input: s = "ab#c", t = "ad#c"
Output: true
Explanation: Both s and t become "ac".
Example 2:

Input: s = "ab##", t = "c#d#"
Output: true
Explanation: Both s and t become "".
Example 3:

Input: s = "a#c", t = "b"
Output: false
Explanation: s becomes "c" while t becomes "b".

https://www.youtube.com/watch?v=k2qrymM_DOo
easy way to use two stack and pop elements if encounter "#" but it will take extra space.
"""


class Solution:
    def backspaceCompare(self, s: str, t: str) -> bool:
        def nexIndex(index, st):
            backspace = 0
            # if have backspace then count no of backspace and decrement index
            # if find an char decrement backspace and decrement index
            # else retrun index.
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
            # get index from above helper methode and check if the value is matching 
            # if any of index value reach 0 then retrun false.
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
