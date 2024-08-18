"""
https://leetcode.com/problems/rearrange-string-k-distance-apart/description/

Given a string s and an integer k, rearrange s such that the same characters are at least distance k from each other. If it is not possible to rearrange the string, return an empty string "".

 

Example 1:

Input: s = "aabbcc", k = 3
Output: "abcabc"
Explanation: The same letters are at least a distance of 3 from each other.
Example 2:

Input: s = "aaabc", k = 3
Output: ""
Explanation: It is not possible to rearrange the string.
Example 3:

Input: s = "aaadbbcc", k = 2
Output: "abacabcd"
Explanation: The same letters are at least a distance of 2 from each other.


"""

class Solution:
    def rearrangeString(self, s: str, k: int) -> str:
        import heapq
        count = Counter(s)
        lst = [(-cnt, val) for val, cnt in count.items()]
        heapq.heapify(lst)
        q = []
        i = -1
        res = ""
        # remove most frequesnt element from the heap and hold it in the queue unless it current index - it previous inserted index >= k, the push it back to heap sothat it will be picked by next iteration.
        while len(lst):
            c, val = heapq.heappop(lst)
            i+=1
            c+=1
            res+=val
            if c<0:
                q.append((c,val, i))
            # hold untill its time comes , read above commet.
            if len(q) and (i-q[0][2]+1)>=k:
                heapq.heappush(lst,(q[0][0],q[0][1]))
                del q[0]
        if len(q)>0:
            return ""
        return res
