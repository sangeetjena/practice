"""
https://leetcode.com/problems/decode-string/?envType=company&envId=google&favoriteSlug=google-thirty-days

Given an encoded string, return its decoded string.

The encoding rule is: k[encoded_string], where the encoded_string inside the square brackets is being repeated exactly k times. 
Note that k is guaranteed to be a positive integer.

You may assume that the input string is always valid; there are no extra white spaces, square brackets are well-formed, etc. Furthermore, 
you may assume that the original data does not contain any digits and that digits are only for those repeat numbers, 
k. For example, there will not be input like 3a or 2[4].

The test cases are generated so that the length of the output will never exceed 105.

 

Example 1:

Input: s = "3[a]2[bc]"
Output: "aaabcbc"
Example 2:

Input: s = "3[a2[c]]"
Output: "accaccacc"
Example 3:

Input: s = "2[abc]3[cd]ef"
Output: "abcabccdcdcdef"


Note: similar to evaluate paranthesis problem.
put element to the stack and pop the element if got an ']'.
1- need to handle few corneor cases like if the number is more than 1 digit then need to extract all number at once and push it to the stack.
2- if the last expression is simple word then hust pop the word and add it to the final word.
"""

from collections import deque
class Solution:
    def decodeString(self, s: str) -> str:
        # it is a stack problem
        # push the elements to the stack and evaluate the element if encounter an ] and push it back to the stack
        stack = deque()
        i = 0
        res = ""
        out = ""
        while i<len(s):
            res=""
            if s[i] == ']':
                print(res, stack)
                # pop all the element untill get '['
                # note: pop will be in the reverse order, so need to handle this.
                while len(stack):
                    elem = stack.pop() 
                    if elem !='[':
                        res = elem + res
                    else:
                        break
            else:
              # to handle the case if the number is more thant single digit then need to pull entire number at once.
                num=0
                if s[i].isdigit():
                    while s[i].isdigit():
                        num = num*10+int(s[i])
                        i+=1
                    stack.append(str(num))
                else:
                    stack.append(s[i])
                    i+=1
                continue
            print(stack)
            i+=1
            lst_elem = stack.pop()
            if lst_elem.isdigit():
                print("{} us a digit".format(lst_elem))
                res = res *int(lst_elem)
            else:
                print("{} is not a digit".format(lst_elem))
                res = lst_elem+res
            # check if the last element is a number or not
            # if it is a number then multiply the char by that time 
            # else just append the car tothe final result.
            # if the stack is empyt then add the value to the output else add it back to the stack.
            if len(stack) == 0:
                out += res
            else:
                stack.append(res)
        res = ""
        while len(stack)>0:
            res = stack.pop() +res
        return out+res

        
