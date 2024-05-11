class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        temp = [nums[i] for i in range(len(nums))]
        for i in range(0, len(nums)):
            temp[(i + k) % len(nums)] = nums[i]
        print(temp)
        for i in range(len(nums)):
            nums[i] = temp[i]
