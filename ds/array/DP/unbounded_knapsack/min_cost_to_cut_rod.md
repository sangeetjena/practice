```
https://leetcode.com/problems/minimum-cost-to-cut-a-stick/description/

Given a wooden stick of length n units. The stick is labelled from 0 to n. For example, a stick of length 6 is labelled as follows:


Given an integer array cuts where cuts[i] denotes a position you should perform a cut at.

You should perform the cuts in order, you can change the order of the cuts as you wish.

The cost of one cut is the length of the stick to be cut, the total cost is the sum of costs of all cuts. When you cut a stick, it will be split into two smaller sticks (i.e. the sum of their lengths is the length of the stick before the cut). Please refer to the first example for a better explanation.

Return the minimum total cost of the cuts.



Note: this has to try with all possible cuts and take the min from them
Option1:-(top down approach) ( mamoisation) 1st take one cut and check what is it s left and right size and cost.
then compare with other cuts and take the min form that cut.
Option2: (bottom up)
```
<img width="747" height="845" alt="image" src="https://github.com/user-attachments/assets/ceb6fcbd-83e3-4907-b95f-76225a5018c6" />
<img width="718" height="173" alt="image" src="https://github.com/user-attachments/assets/c3ed3b54-d0c9-4f07-99ec-43f53ce699c2" />


``` python
class Solution:
    
    def minCost(self, n: int, cuts: List[int]) -> int:
        dp = {}
        def dfs(l,r):
            if l-r==1:
                return 0
            if (l,r) in dp.keys():
                return dp[(l,r)]
            res = float("inf")
            for cut in cuts:

                if l<cut<r:
                    res = min(res, (r-l) + dfs(l,cut) + dfs(cut,r))
            dp[(l,r)] = 0 if res == float("inf") else res
            return dp[(l,r)]
        return dfs(0,n)
```
