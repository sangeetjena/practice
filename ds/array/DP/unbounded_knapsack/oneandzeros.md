```
https://leetcode.com/problems/ones-and-zeroes/description/?envType=company&envId=google&favoriteSlug=google-thirty-days



You are given an array of binary strings strs and two integers m and n.

Return the size of the largest subset of strs such that there are at most m 0's and n 1's in the subset.

A set x is a subset of a set y if all elements of x are also elements of y.



```

<img width="1047" height="601" alt="image" src="https://github.com/user-attachments/assets/97e4e34c-aef0-451a-85f2-1eb6d94d0a7e" />


``` python

class Solution:
    def findMaxForm(self, strs: List[str], m: int, n: int) -> int:
        dp = {(0,0):0}
        atleast_one = 0
        for elem in strs:
            one, zero= 0, 0
            for i in range(len(elem)):
                if elem[i] == '0':
                    zero+=1
                else:
                    one+=1
            # in python dictionary can't change the size while iteration so creating a temp dictonary
            tempdp = {}
            for k,v in dp.items():
        
                prevone, prevzero = k
                newone, newzero = prevone + one, prevzero + zero
                if newone<=n and newzero<=m:
                    if (newone, newzero) not in dp:
                        tempdp[(newone, newzero)] = v+1
                    elif dp[(newone, newzero)] < v+1:
                        tempdp[(newone, newzero)] = v+1
            dp.update(tempdp)
        print(dp)
        return max([dp[key] for key in dp.keys()])



```
