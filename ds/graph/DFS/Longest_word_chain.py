"""
https://leetcode.com/problems/longest-string-chain/description/?envType=problem-list-v2&envId=two-pointers

You are given an array of words where each word consists of lowercase English letters.

wordA is a predecessor of wordB if and only if we can insert exactly one letter anywhere in wordA without changing the order of the other characters to make it equal to wordB.

For example, "abc" is a predecessor of "abac", while "cba" is not a predecessor of "bcad".
A word chain is a sequence of words [word1, word2, ..., wordk] with k >= 1, where word1 is a predecessor of word2, word2 is a predecessor of word3, and so on. A single word is trivially a word chain with k == 1.

Return the length of the longest possible word chain with words chosen from the given list of words.

 

Example 1:

Input: words = ["a","b","ba","bca","bda","bdca"]
Output: 4
Explanation: One of the longest word chains is ["a","ba","bda","bdca"].
Example 2:

Input: words = ["xbc","pcxbcf","xb","cxbc","pcxbc"]
Output: 5
Explanation: All the words can be put in a word chain ["xb", "xbc", "cxbc", "pcxbc", "pcxbcf"].
Example 3:

Input: words = ["abcd","dbqca"]
Output: 1
Explanation: The trivial word chain ["abcd"] is one of the longest word chains.
["abcd","dbqca"] is not a valid word chain because the ordering of the letters is changed.


Note: step1: calculate inplace replacement patterns i.e len(word) = len(word replacement *)
      step 2: dfs -> find pattern expanded patterns i.e len(pattern) = len(word)+1 -> ab -> pattern *ab, a*b, ab*
"""

class Solution:
    def longestStrChain(self, words: List[str]) -> int:
        words.sort()
        print(words)
        visited = []
        dfs = []
        all_words = defaultdict(list)
        mx_len = 1
        # pre calculate all inplace * replacement patterns
        for word in words:
            # in place * placement ex: abc -> patterns = *bc, a*c, ab*
            for i in range(len(word)):
                wd = word[:i]+"*"+word[i+1:]
                all_words[wd].append(word)
        for word in words:
            if word not in visited:
                dfs.append((word,1))
            circular_visit = set()
            while dfs:
                wd,ln = dfs[-1]
                mx_len = max(mx_len, ln)
                if wd in circular_visit:
                    del dfs[-1]
                    # below allow to research path from other other node but causing time limit exceeding 
                    # circular_visit.remove(wd) 
                    continue
                circular_visit.add(wd)
                for i in range(len(wd)+1):
                    # expand and place *  ex: ab -> pattern *ab, a*b, ab*
                    pat = wd[:i]+"*"+wd[i:] 
                    for temp_word in all_words[pat]:
                        if temp_word not in circular_visit:
                            dfs.append((temp_word,ln+1))
                visited.append(wd)
                
        return mx_len


        
