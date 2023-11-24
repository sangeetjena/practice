"""
Given two strings text1 and text2, return the length of their longest common subsequence. If there is no common subsequence, return 0.

A subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

For example, "ace" is a subsequence of "abcde".
A common subsequence of two strings is a subsequence that is common to both strings.



Example 1:

Input: text1 = "abcde", text2 = "ace"
Output: 3
Explanation: The longest common subsequence is "ace" and its length is 3.
Example 2:

Input: text1 = "abc", text2 = "abc"
Output: 3
Explanation: The longest common subsequence is "abc" and its length is 3.
Example 3:

Input: text1 = "abc", text2 = "def"
Output: 0
Explanation: There is no such common subsequence, so the result is 0.

Link: https://www.youtube.com/watch?v=0yvOxPwe3Dg&t=342s
"""

def lcs(arr1, arr2):
    if len(arr1) == 0 or len(arr2) == 0:
        return 0
    if( arr1[-1] == arr2[-1]):
        return 1 + lcs(arr1[:len(arr1)-1], arr2[:len(arr2)-1])
    return max(lcs(arr1[:len(arr1)-1], arr2), lcs(arr1, arr2[:len(arr2)-1]))

print(lcs("abc","def"))
print(lcs("abc","abc"))
print(lcs("abcde","ace"))