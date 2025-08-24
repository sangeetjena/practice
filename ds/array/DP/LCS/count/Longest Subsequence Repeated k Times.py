"""
https://leetcode.com/problems/longest-subsequence-repeated-k-times/description/

You are given a string s of length n, and an integer k. You are tasked to find the longest subsequence repeated k times in string s.

A subsequence is a string that can be derived from another string by deleting some or no characters without changing the order of the remaining characters.

A subsequence seq is repeated k times in the string s if seq * k is a subsequence of s, where seq * k represents a string constructed by concatenating seq k times.

For example, "bba" is repeated 2 times in the string "bababcba", because the string "bbabba", constructed by concatenating "bba" 2 times, is a subsequence of the string "bababcba".
Return the longest subsequence repeated k times in string s. If multiple such subsequences are found, return the lexicographically largest one. If there is no such subsequence, return an empty string.

 

Example 1:

example 1
Input: s = "letsleetcode", k = 2
Output: "let"
Explanation: There are two longest subsequences repeated 2 times: "let" and "ete".
"let" is the lexicographically largest one.
Example 2:

Input: s = "bb", k = 2
Output: "b"
Explanation: The longest subsequence repeated 2 times is "b".
Example 3:

Input: s = "ab", k = 2
Output: ""
Explanation: There is no subsequence repeated 2 times. Empty string is returned.


Note: Take frequency of the charactor and then use bfs to get in lexicographical order , form all possible string in the tree and check if subsequence is possible or not.
if possible then add it to the bfs.

also only consider those charector whose frequency is greter than or equals to k. because if frequency is lesser than k then that many time words can't be formed.
"""

class Solution:
    def isKRepeatedSubsequence(self, s: str, pattern: str, k: int) -> bool:
        pos = matched = 0
        m = len(pattern)
        for ch in s:
            if ch == pattern[pos]:
                pos += 1
                if pos == m:
                    pos = 0
                    matched += 1
                    if matched == k:
                        return True
        return False

    def longestSubsequenceRepeatedK(self, s: str, k: int) -> str:
        freq = [0]*26
        for ch in s:
            freq[ord(ch)-97] += 1
        candidates = [chr(i+97) for i in range(25, -1, -1) if freq[i] >= k]

        q = deque(candidates)
        ans = ""

        while q:
            curr = q.popleft()
            if len(curr) > len(ans) or (len(curr) == len(ans) and curr > ans):
                if self.isKRepeatedSubsequence(s, curr, k):
                    ans = curr
            if len(curr) == 7:
                continue
            for ch in candidates:
                nxt = curr + ch
                if self.isKRepeatedSubsequence(s, nxt, k):
                    q.append(nxt)
        return ans
