"""
https://leetcode.com/problems/find-the-shortest-superstring/description/

Given an array of strings words, return the smallest string that contains each string in words as a substring. If there are multiple valid strings of the smallest length, return any of them.

You may assume that no string in words is a substring of another string in words.

 

Example 1:

Input: words = ["alex","loves","leetcode"]
Output: "alexlovesleetcode"
Explanation: All permutations of "alex","loves","leetcode" would also be accepted.
Example 2:

Input: words = ["catg","ctaagt","gcta","ttca","atgcatc"]
Output: "gctaagttcatgcatc"


Note: this is similar to travelling sales man, where we need to find all possible combination sequence of word to merge. and from all the combination we have to find the min
length.
"""
