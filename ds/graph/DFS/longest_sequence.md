```
https://leetcode.com/problems/longest-consecutive-sequence/description/

Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence.

You must write an algorithm that runs in O(n) time.

 

Example 1:

Input: nums = [100,4,200,1,3,2]
Output: 4
Explanation: The longest consecutive elements sequence is [1, 2, 3, 4]. Therefore its length is 4.
Example 2:

Input: nums = [0,3,7,2,5,8,4,6,0,1]
Output: 9
Example 3:

Input: nums = [1,0,1,2]
Output: 3



Note: simple solution is take one element and add one, and check if next number present.
keep track of max length sequence.
```


``` python
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        num_set = set(nums)
        longest = 0
        visited = []
        for n in num_set:
            # check if previous number exists, then that would have already traverssed , so no need to travers again.
            # or if n-1 is number is there then that will do the final traversal, this element can igore traversal.
            # else min length will start with len 1.
            if n - 1 not in num_set:
                length = 1
                # look for next element by adding 1
                while n + length in num_set:
                    length += 1
                
                longest = max(longest, length)
        
        return longest
```

```

class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        dct = {}
        for elem in nums:
            dct[elem] = 1
        visited = []
        max_len = 0
        for elem in nums:
            if elem in visited:
                continue
            temp_len = 0 
            while elem in dct.keys():
                temp_len+=1
                visited.append(elem)
                elem+=1
            max_len = max(max_len,  temp_len)
        return max_len
    ```
        
