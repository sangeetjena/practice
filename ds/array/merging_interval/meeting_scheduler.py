"""
https://leetcode.com/problems/meeting-scheduler/?envType=problem-list-v2&envId=two-pointers
Given the availability time slots arrays slots1 and slots2 of two people and a meeting duration duration, return the earliest time slot that works for both of them and is of duration duration.

If there is no common time slot that satisfies the requirements, return an empty array.

The format of a time slot is an array of two elements [start, end] representing an inclusive time range from start to end.

It is guaranteed that no two availability slots of the same person intersect with each other. That is, for any two time slots [start1, end1] and [start2, end2] of the same person, either start1 > end2 or start2 > end1.

 

Example 1:

Input: slots1 = [[10,50],[60,120],[140,210]], slots2 = [[0,15],[60,70]], duration = 8
Output: [60,68]
Example 2:

Input: slots1 = [[10,50],[60,120],[140,210]], slots2 = [[0,15],[60,70]], duration = 12
Output: []


Note: similar to max platform needed.

"""
class Solution:
    def minAvailableDuration(self, slots1: List[List[int]], slots2: List[List[int]], duration: int) -> List[int]:
        i,j = 0,0
        # times not sorted 
        slots1.sort()
        slots2.sort()
        while i< len(slots1) and j < len(slots2):
            s1_s = slots1[i][0]
            s1_e = slots1[i][1]
            s2_s = slots2[j][0]
            s2_e = slots2[j][1]
            print(i,j)
            if (  s2_s < s1_s < s2_e or   s2_s < s1_e < s2_e or s1_s < s2_s < s1_e or   s1_s < s2_e < s1_e
            or (s1_s == s2_s and s1_e == s2_e)):
                maxdiff = min(s2_e, s1_e) - max(s1_s, s2_s)
                print(maxdiff)
                if maxdiff>=duration:
                    return [max(s1_s, s2_s), max(s1_s, s2_s)+duration]
            # move smallest end forward.
            if s1_e > s2_e:
                j+=1
            else:
                i+=1
        return []
