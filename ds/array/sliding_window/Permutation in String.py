"""
https://leetcode.com/problems/permutation-in-string/description/

Create a HashMap to calculate the frequencies of all characters in the pattern.
Iterate through the string, adding one character at a time in the sliding window.
If the character being added matches a character in the HashMap, decrement its frequency in the map. If the character frequency becomes zero, we got a complete match.
If at any time, the number of characters matched is equal to the number of distinct characters in the pattern (i.e., total characters in the HashMap), we have gotten our required permutation.
If the window size is greater than the length of the pattern, shrink the window to make it equal to the patterns size. At the same time, if the character going out was part of the pattern, put it back in the frequency HashMap.
"""

class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        tempdp = {}
        for i in s1:
            if i in tempdp.keys():
                tempdp[i]+=1
            else:
                tempdp[i] = 1
        end = start =0
        while end < len(s2):
            if s2[end] in tempdp.keys():
                tempdp[s2[end]]-=1
            # if window size corss the len of s1 then increament the start and increment char count in the dict
            if end-start+1 > len(s1):
                if s2[start] in tempdp.keys():
                    tempdp[s2[start]]+=1
                start+=1
            # if ablove condition pass and window size is within the thereshold and all values
            # of the dict key is 0 that means all char of s1 is found in the given window of s2.
            print(tempdp,start, end, (end-start+1))
            if all(values==0 for values in tempdp.values()):
                return True
            end+=1
        return False
        
