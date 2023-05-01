"""
Given an integer array nums that may contain duplicates, return all possible
subsets
 (the power set).

The solution set must not contain duplicate subsets. Return the solution in any order.



Example 1:

Input: nums = [1,2,2]
Output: [[],[1],[1,2],[1,2,2],[2],[2,2]]
"""
import copy
class Solution:
    def __init__(self):
        self.all_combination = []
    # using recursion
    def combination(self,n, set, ind, currentcombination):
        print("-----")
        print(currentcombination)
        if currentcombination not in self.all_combination:
            print("added to all_combination")
            self.all_combination.append(copy.deepcopy(currentcombination))
            print(self.all_combination)

        for i in range(ind,len(set)):
            currentcombination.append(set[i])
            self.combination(n,set,i+1 ,copy.deepcopy(currentcombination))
            currentcombination.pop()


obj = Solution()
obj.combination(2,[1,2,2],0, [])
print(obj.all_combination)



