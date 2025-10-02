"""
https://leetcode.com/problems/smallest-range-covering-elements-from-k-lists/description/

You have k lists of sorted integers in non-decreasing order. Find the smallest range that includes at least one number from each of the k lists.

We define the range [a, b] is smaller than range [c, d] if b - a < d - c or a < c if b - a == d - c.

 

Example 1:

Input: nums = [[4,10,15,24,26],[0,9,12,20],[5,18,22,30]]
Output: [20,24]
Explanation: 
List 1: [4, 10, 15, 24,26], 24 is in range [20,24].
List 2: [0, 9, 12, 20], 20 is in range [20,24].
List 3: [5, 18, 22, 30], 22 is in range [20,24].
Example 2:

Input: nums = [[1,2,3],[1,2,3],[1,2,3]]
Output: [1,1]

Note:
tips: find min and max between all arrays in each iteration.
# put all 1st element form each list
# then extract smallest element and take next element and check if min and max value changes or not
# break the loop once one list reached to the end length and return min difference between min and max

"""
import heapq
class Solution:
    def smallestRange(self, nums: List[List[int]]) -> List[int]:
        # put all 1st element form each list
        # then extract smallest element and take next element and check if min and max value changes or not
        # break the loop once one list reached to the end length and return min difference between min and max
        temp = []
        mn,mx = 0,0
        ret = [0,float("inf")]
        for i in range(len(nums)):
            heapq.heappush(temp,(nums[i][0],i,0))
        # current heap max value
        mx = max(temp)[0]
        print(mx)
        while len(temp)>0:
            # find current heap min and max value
            mn, arrind, ind = heapq.heappop(temp)
            #calculate new range with current min and max value in heap ( i.e previous calculated max)
            if ret[1]-ret[0] > mx-mn:
                ret = [mn,mx]
            # any of the list reached to the end of length. that is the end of program.
            if len(nums[arrind])<=ind+1:
                break
            heapq.heappush(temp,(nums[arrind][ind+1], arrind, ind+1))
            # update max heap: if new value creating new max in heap capture it.
            if mx< nums[arrind][ind+1]:
                mx = nums[arrind][ind+1]
        return ret
            
            

        
