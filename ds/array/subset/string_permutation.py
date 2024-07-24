"""
https://leetcode.com/problems/letter-case-permutation/
# back tracking
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
        
