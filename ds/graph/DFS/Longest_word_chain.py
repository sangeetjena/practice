"""
https://leetcode.com/problems/longest-string-chain/description/?envType=problem-list-v2&envId=two-pointers

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


        
