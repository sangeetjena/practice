"""


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
