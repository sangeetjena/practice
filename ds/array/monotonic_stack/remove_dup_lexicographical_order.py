"""
https://leetcode.com/problems/remove-duplicate-letters/description/?envType=problem-list-v2&envId=monotonic-stack

Given a string s, remove duplicate letters so that every letter appears once and only once. 
You must make sure your result is the smallest in lexicographical order among all possible results.

 

Example 1:

Input: s = "bcabc"
Output: "abc"
Example 2:

Input: s = "cbacdcbc"
Output: "acdb"
 

Note: 
# classic problem in monotonic stack: this also can be solved using lcs https://leetcode.com/problems/smallest-subsequence-of-distinct-characters/
        # simple rulse is : 1) if we get a char which is smaller than it previous vaue in the stack and it previous value 
        has suplicate at greader index position in the string then stack[-1] value can be removed
        # rule 2: check if in the stack is the char already exist then no need to do anything.
        # rule 3: break mstack loop if last element not able to delete.
"""
class Solution:
    def removeDuplicateLetters(self, s: str) -> str:
        # classic problem in monotonic stack: this also can be solved using lcs https://leetcode.com/problems/smallest-subsequence-of-distinct-characters/
        # simple rulse is : 1) if we get a char which is smaller than it previous vaue in the stack and it previous value has suplicate at greader index position in the string then stack[-1] value can be removed
        # rule 2: check if in the stack is the char already exist then no need to do anything.
        mstack = []
        for i in range(len(s)):
            # check if the current char is smaller than last value in the stack and if the value not already present in the stack( i.e already processed)
            while mstack and s[i]< mstack[-1] and s[i] not in mstack:
                if mstack[-1] in s[i:]:
                    del mstack[-1]
                else:
                    # why to break ? because value in the stack are present in increaing order(i.e last element is biggest ), if we are not able to delete last element (because unique valur) and after that duplicate elements are there which is bigger in size than s[i] and if we will delete them then the bigest element is there that will 1st take the leading position and if it happens then the world will be lexicographically bigger insteed of smaller) . so if we are not able to delete stack[-1] position then break it
                    break
            # before adding to the stack check if this element is already present in teh stack.
            if s[i] not in (mstack):
                mstack.append(s[i])
        return "".join(mstack)
