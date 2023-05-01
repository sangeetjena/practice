"""
There is a group of n members, and a list of various crimes they could commit. The ith crime generates a profit[i] and requires group[i] members to participate in it. If a member participates in one crime, that member can't participate in another crime.

Let's call a profitable scheme any subset of these crimes that generates at least minProfit profit, and the total number of members participating in that subset of crimes is at most n.

Return the number of schemes that can be chosen. Since the answer may be very large, return it modulo 109 + 7.



Example 1:

Input: n = 5, minProfit = 3, group = [2,2], profit = [2,3]
Output: 2
Explanation: To make a profit of at least 3, the group could either commit crimes 0 and 1, or just crime 1.
In total, there are 2 schemes.
Example 2:

Input: n = 10, minProfit = 5, group = [2,3,5], profit = [6,7,8]
Output: 7
Explanation: To make a profit of at least 5, the group could commit any crimes, as long as they commit one.
There are 7 possible schemes: (0), (1), (2), (0,1), (0,2), (1,2), and (0,1,2).

"""
from typing import List



# Note: this is combination problem. howmany way we can form the group sothat total profit will > min profit
# and maximum people is needed is < n
class Solution:
    combinations = []
    def backtrack(self, arr, start_index, current_combination, combination_length):
        if len(current_combination) == combination_length:
            self.combinations.append(list(current_combination))
            return
        for i in range(start_index, len(arr)):
            current_combination.append(arr[i])
            self.backtrack(i + 1, current_combination)
            current_combination.pop()

    def profitableSchemes(self, n: int, minProfit: int, group: List[int], profit: List[int]) -> int:
        self.combinations = []
        profitable = []
        totalpeople = 0
        totalprofit = 0
        for i in range(len(profit)):
            if profit[i] >= minProfit and group[i]< n:
                profitable.append(profit[i])
            for y in range(i ,len(profit)):
                if i == y:
                    continue
                if group[i] + group[y] <= n and profit[i] + profit[y] >= minProfit:
                    profitable.append((profit[i], profit[y]))
        print(profitable)
        return len(profitable)

obj = Solution()
resp = obj.profitableSchemes(n = 10, minProfit = 5, group = [2,3,5], profit = [6,7,8])
print(resp)