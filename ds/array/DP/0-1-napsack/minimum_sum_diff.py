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
overal time comlexity = (2^n/2 *n/2)


how it is different from subset sum equal to k:
here in this question it has asked max sub set sum which is closer to the sum target. 

youtube: https://www.youtube.com/watch?v=naz_9njI0I0

"""
