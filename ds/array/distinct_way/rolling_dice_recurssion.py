"""
https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/
https://www.youtube.com/watch?v=hfUxjdjVQN4&t=1s
"""


class Solution:
    def numRollsToTarget(self, n: int, k: int, target: int) -> int:
        mod = 10 ** 9 + 7
        catche = {}

        def count(n, target):
            if n == 0:
                return 1 if target == 0 else 0
            if (n, target) in catche:
                return catche[(n, target)]
            res = 0
            for i in range(1, k + 1):
                res = (res + count(n - 1, target - i)) % mod
            catche[(n, target)] = res
            return res
        return count(n, target)

