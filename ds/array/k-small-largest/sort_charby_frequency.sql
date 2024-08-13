"""
https://leetcode.com/problems/sort-characters-by-frequency/description/

Given a string s, sort it in decreasing order based on the frequency of the characters. The frequency of a character is the number of times it appears in the string.

Return the sorted string. If there are multiple answers, return any of them.

 

Example 1:

Input: s = "tree"
Output: "eert"
Explanation: 'e' appears twice while 'r' and 't' both appear once.
So 'e' must appear before both 'r' and 't'. Therefore "eetr" is also a valid answer.
Example 2:
Input: s = "Aabb"
Output: "bbAa"
Explanation: "bbaA" is also a valid answer, but "Aabb" is incorrect.
Note that 'A' and 'a' are treated as two different characters.

"""

class Solution:
    def frequencySort(self, s: str) -> str:
        import heapq
        dct = {}
        out = ""
        for x in s:
            if x in dct.keys():
                dct[x]+=1
            else:
                dct[x]=1
        lst = [(-dct[key], key) for key in dct.keys()]
        print(lst)
        heapq.heapify(lst)
        for i in range(len(lst)):
            cnt, elem = heapq.heappop(lst)
            cnt = cnt*-1
            for i in range(cnt):
                out+=elem
            
        return out
