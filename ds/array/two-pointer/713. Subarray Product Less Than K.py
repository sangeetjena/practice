"""
https://leetcode.com/problems/subarray-product-less-than-k/description/
https://www.youtube.com/watch?v=Cg6_nF7YIks
"""


class Solution:
    def numSubarrayProductLessThanK(self, nums: List[int], k: int) -> int:
        if k <= 1:
            return 0

        count = 0
        product = 1
        i, j = 0, 0

        while j < len(nums):
            product = product * nums[j]
            if product < k:
                # formula : the total window we will add that many subarray it will form.
                count = count + (j - i + 1)
            elif product >= k:
                while product >= k:
                    product = product // nums[i]
                    i = i + 1
                # formula: the total window we will add that many subarray it will form.
                count = count + (j - i + 1)
            j = j + 1

        return count
