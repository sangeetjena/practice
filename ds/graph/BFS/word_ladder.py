"""
https://leetcode.com/problems/word-ladder/description/

A transformation sequence from word beginWord to word endWord using a dictionary wordList is a sequence of words beginWord -> s1 -> s2 -> ... -> sk such that:

Every adjacent pair of words differs by a single letter.
Every si for 1 <= i <= k is in wordList. Note that beginWord does not need to be in wordList.
sk == endWord
Given two words, beginWord and endWord, and a dictionary wordList, return the number of words in the shortest transformation sequence from beginWord to endWord, or 0 if no such sequence exists.

 

Example 1:

Input: beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]
Output: 5
Explanation: One shortest transformation sequence is "hit" -> "hot" -> "dot" -> "dog" -> cog", which is 5 words long.
Example 2:

Input: beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log"]
Output: 0
Explanation: The endWord "cog" is not in wordList, therefore there is no valid transformation sequence.

Note: find all the regex and store that as the key in dictionary , then create prefix  set and construct graph and then run bfs.
"""

from collections import deque
class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
        pattern = defaultdict(list)
        for word in wordList:
            for i in range(len(word)):
                pat = word[:i] + '*' + word[i+1:]
                pattern[pat].append(word)
        # find a word and it all possible pattern
        # then check in that pattern what are all words that the present word can go next.
        print(pattern)
        queue = deque([(beginWord,1)])
        mincnt = 999999
        visited = []
        # common bfs pattern
        while len(queue)>0:
            currWord, cnt = queue.popleft()
            if currWord == endWord:
                print(currWord, endWord, cnt, mincnt)
                mincnt = min(mincnt,cnt)
            if currWord in visited:
                continue
            
            # find all patterns for the word
            for i in range(len(currWord)):
                pat = currWord[:i] + '*' + currWord[i+1:]
                for words in pattern[pat]:
                    if words in visited:
                        continue
                    queue.append((words,cnt+1))
            visited.append(currWord)
        return mincnt if mincnt!=999999 else 0
