"""
Given an input string s and a pattern p, implement regular expression matching with support for '.' and '*' where:

'.' Matches any single character.​​​​
'*' Matches zero or more of the preceding element.
The matching should cover the entire input string (not partial).



Example 1:

Input: s = "aa", p = "a"
Output: false
Explanation: "a" does not match the entire string "aa".
Example 2:

Input: s = "aa", p = "a*"
Output: true
Explanation: '*' means zero or more of the preceding element, 'a'. Therefore, by repeating 'a' once, it becomes "aa".
Example 3:

Input: s = "ab", p = ".*"
Output: true
Explanation: ".*" means "zero or more (*) of any character (.)".

"""

class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        catch = ""
        reset = 0
        if len(s)==0:
            return False
        if '.' not in p and '*' not in p and s != p:
            return False
        for char in p:
            if char in ['.','*']:
                reset = 1
                if char == '.':
                    if s[:len(catch)] == catch and len(s)>len(catch):
                        s = s[:len(catch)]
                        continue
                    else:
                        return False
                if len(catch) == 0:  #case: when expression starts with *, ex: *abc
                    continue
                if s[:len(catch)] == catch:
                    return True
                else:
                    return False
            else:
                if reset == 1:
                    catch = ""
                catch += char
                reset = 0
        print(catch)
        print(s[len(s) - len(catch):])
        if catch == s[len(s) - len(catch):]:
            return True
        else:
            return False

obj = Solution()
s = ["aa","aa", "", "abcd", "a"]
p = ["a","a*", "a*","*bc", "a*."]
for i in range(len(s)):
    print(p[i], s[i])
    resp = obj.isMatch(s[i], p[i])
    if resp == True:
        print("pass")
    else:
        print("fail")