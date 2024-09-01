"""


"""
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        dp = [[0 for i in range(k+1)] for _ in range(len(nums)+1)]
        dp[0][0]=1
        for i in range(1,len(nums)+1):
            for j in range(k+1):
                if nums[i-1]<=j:
                    dp[i][j] = dp[i-1][j] + dp[i-1][j-nums[i-1]]
                else:
                    dp[i][j] = dp[i-1][j] 
        print(dp)
        return dp[-1][-1]

print(sub_set_sum_equals_to_k([3,2,3,5,4,5], 5))

print(sub_set_sum_equals_to_k([3,2,3,5,4,5], 10))
