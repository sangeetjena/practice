"""
https://leetcode.com/problems/substring-with-concatenation-of-all-words/

You are given a string s and an array of strings words. All the strings of words are of the same length.

A concatenated string is a string that exactly contains all the strings of any permutation of words concatenated.

For example, if words = ["ab","cd","ef"], then "abcdef", "abefcd", "cdabef", "cdefab", "efabcd", and "efcdab" are all concatenated strings. "acdbef" is not a concatenated string because it is not the concatenation of any permutation of words.
Return an array of the starting indices of all the concatenated substrings in s. You can return the answer in any order.

 

Example 1:

Input: s = "barfoothefoobarman", words = ["foo","bar"]

Output: [0,9]

Explanation:

The substring starting at 0 is "barfoo". It is the concatenation of ["bar","foo"] which is a permutation of words.
The substring starting at 9 is "foobar". It is the concatenation of ["foo","bar"] which is a permutation of words.



Note:
This is similar to the permutation string, only difference is register the starting pointer whenever find a mathcing permutation and need to match word insteed of char.

""""

import copy
class Solution:
    def findSubstring(self, s: str, words: List[str]) -> List[int]:
        dct = {}
        for word in words:
            if word in dct.keys():
                dct[word]+=1
            else:
                dct[word]=1
        l = len(words[0])
        st=0
        ed = 0 
        total = []
        tmpdct = copy.deepcopy(dct)
        while ed < len(s) and st< len(s):
            wd = s[ed:ed+l]
            # print(wd,st,ed,s, total)
            # case for unmatch word or breaking sequence
            if wd in tmpdct.keys():
                tmpdct[wd]-=1
            else:
                tmpdct = copy.deepcopy(dct)
                st = st+1
                ed=st
                continue
            # if all match then increse total and increment start and remove one frequency of the starting char
            if all(val == 0 for val in tmpdct.values()):
                total.append(st)
                # tmpdct[s[st:st+l]]+=1
                # st+=l
                tmpdct = copy.deepcopy(dct)
                st = st+1
                ed = st
                continue
            if any(val<0 for val in tmpdct.values()):
                tmpdct = copy.deepcopy(dct)
                st = st+1
                ed = st
                continue

            # if any -ve char came remove char form begining untill -ve frequency removed from dct
            # while any(val<0 for val in tmpdct.values()):
            #     tmpdct[s[st:st+l]]+=1
            #     st+=l
            # print(tmpdct, dct)
            ed+=l
        return total
            

            
