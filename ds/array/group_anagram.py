"""
https://leetcode.com/problems/group-anagrams/
"""


class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        anagrams = {}
        for ana in strs:
            srt = "".join(sorted(ana))
            if srt not in anagrams.keys():
                anagrams[srt] = [ana]
            else:
                anagrams[srt].append(ana)
        x = []
        for key in anagrams.keys():
            x.append(anagrams[key])
        return x
