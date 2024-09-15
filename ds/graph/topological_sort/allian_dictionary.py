"""
https://leetcode.com/problems/alien-dictionary/description/

Node: used dfs but also can be solved using in-degree.

There is a new alien language that uses the English alphabet. However, the order of the letters is unknown to you.

You are given a list of strings words from the alien language's dictionary. Now it is claimed that the strings in words are 
sorted lexicographically
 by the rules of this new language.

If this claim is incorrect, and the given arrangement of string in words cannot correspond to any order of letters, return "".

Otherwise, return a string of the unique letters in the new alien language sorted in lexicographically increasing order by the new language's rules. If there are multiple solutions, return any of them.

 

Example 1:

Input: words = ["wrt","wrf","er","ett","rftt"]
Output: "wertf"
Example 2:

Input: words = ["z","x"]
Output: "zx"
Example 3:

Input: words = ["z","x","z"]
Output: ""
Explanation: The order is invalid, so return "".
"""
class Solution:
    def alienOrder(self, words: List[str]) -> str:
        dct = {}
        any_relation = 0
        # initialize all char with empty list sothat in dfs it will parse all keys.
        for word in words:
            for i in range(len(word)):
                dct[word[i]]=[]
        for i in range(1, len(words)):
            rng = min(len(words[i-1]), len(words[i]))
            for j in range(rng):
                c1, c2  = words[i-1][j],  words[i][j]
                # check for first missmatch value in word1 and word2 at same index.
                # need not to match all char as lowest index char decide ordering in dictioinary.
                if  c1 != c2:
                    dct[c1].append(c2)
                    break
            #corner case if all char match and word1 len is lesser than word 2 then can't determine ordering.
            else:
                if len(words[i]) < len(words[i-1]):
                    return ""
        # rest is same as topological sort.       
        dfs = []
        visited = []
        cycle = set([])
        out = ""
        for key in dct.keys():
            if key in visited:
                continue
            dfs.append(key)
            while len(dfs) > 0:
                node = dfs[-1]
                cycle.add(node)
                if node in visited:
                    del dfs[-1]
                    cycle.remove(node)
                    if node not in out:
                        # reverse ordering as we need to print child 1st.
                        out=node+out
                    continue
                for chld in dct[node]:
                    if chld in cycle:
                        return ""
                    dfs.append(chld)
                visited.append(node)
        return out

=================


from collections import defaultdict, Counter, deque

def alienOrder(self, words: List[str]) -> str:
    
    # Step 0: create data structures + the in_degree of each unique letter to 0.
    adj_list = defaultdict(set)
    in_degree = Counter({c : 0 for word in words for c in word})
            
    # Step 1: We need to populate adj_list and in_degree.
    # For each pair of adjacent words...
    for first_word, second_word in zip(words, words[1:]):
        for c, d in zip(first_word, second_word):
            if c != d:
                if d not in adj_list[c]:
                    adj_list[c].add(d)
                    in_degree[d] += 1
                break
        else: # Check that second word isn't a prefix of first word.
            if len(second_word) < len(first_word): return ""
    
    # Step 2: We need to repeatedly pick off nodes with an indegree of 0.
    output = []
    queue = deque([c for c in in_degree if in_degree[c] == 0])
    while queue:
        c = queue.popleft()
        output.append(c)
        for d in adj_list[c]:
            in_degree[d] -= 1
            if in_degree[d] == 0:
                queue.append(d)
                
    # If not all letters are in output, that means there was a cycle and so
    # no valid ordering. Return "" as per the problem description.
    if len(output) < len(in_degree):
        return ""
    # Otherwise, convert the ordering we found into a string and return it.
    return "".join(output)
