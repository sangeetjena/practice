"""
https://leetcode.com/problems/partition-array-into-two-arrays-to-minimize-sum-difference/description/

You are given an integer array nums of 2 * n integers. You need to partition nums into two arrays of length n to minimize the absolute difference of the sums of the arrays. To partition nums, put each element of nums into one of the two arrays.

Return the minimum possible absolute difference.

 

Example 1:

example-1
Input: nums = [3,9,7,3]
Output: 2
Explanation: One optimal partition is: [3,9] and [7,3].
The absolute difference between the sums of the arrays is abs((3 + 9) - (7 + 3)) = 2.

Note: meet at the middle.
approah 1: (compexity = 2^n) bruite force solution: find all subset sum. represetn intin a tiem line and find the sum closest to the target sum. 
approach 2:( optimization on top of the above approach)  devide the array into two set and find each possible subset in the devided array. 
so here to reduce the time complexity we devide the set to two and find all sum possible in two set separately.
then take two pointer approach and keep one pointer in set 1 and find the second element in the second set. to to find the sexond element 
in the second set use binary search.
overal time comlexity = (2^n/2 *n/2) = 2^n ( no differene between bruteforce solution)
approch 3:
enhancing on top of approach2 but insteed of searching all the elements in teh set2. we can use biniary search to find the most closest element.

how it is different from subset sum equal to k:
here in this question it has asked max sub set sum which is closer to the sum target. 

youtube: https://www.youtube.com/watch?v=naz_9njI0I0

"""

class Solution:
    def minimumDifference(self, nums: List[int]) -> int:
        N = len(nums) // 2 # Note this is N/2, ie no. of elements required in each.
        
        def get_sums(nums): # generate all combinations sum of k elements
            ans = {}
            N = len(nums)
            for k in range(1, N+1): # takes k element for nums
                sums = []
                for comb in combinations(nums, k):
                    s = sum(comb)
                    sums.append(s)
                ans[k] = sums
            return ans
        # note: why deviding nums to half will work here, because in the below logic we are taking one sum from left and trying to find closest sum from right to reach closest to total/2 and that will give a result for lest subset. ( so indirectly we are finding all combination but deviding full set to two to reduce computation)
        left_part, right_part = nums[:N], nums[N:]
        left_sums, right_sums = get_sums(left_part), get_sums(right_part)
        ans = abs(sum(left_part) - sum(right_part)) # the case when taking all N from left_part for left_ans, and vice versa
        total = sum(nums) 
        half = total // 2 # the best sum required for each, we have to find sum nearest to this
        for k in range(1, N):
            left = left_sums[k] # if taking k no. from left_sums
            right = right_sums[N-k] # then we have to take remaining N-k from right_sums.
            print(left, right)
            right.sort() # sorting, so that we can binary search the required value
            for x in left:
                print(x)
                r = half - x # required, how much we need to add in x to bring it closer to half.
                p = bisect.bisect_left(right, r) # we are finding index of value closest to r, present in right, using binary search
                for q in [p, p-1]:
                    if 0 <= q < len(right):
                        left_ans_sum = x + right[q]
                        right_ans_sum = total - left_ans_sum
                        diff = abs(left_ans_sum - right_ans_sum)
                        ans = min(ans, diff) 
        return ans
