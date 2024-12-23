"""
https://leetcode.com/problems/decode-string/?envType=company&envId=google&favoriteSlug=google-thirty-days


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

        
