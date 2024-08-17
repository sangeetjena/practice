"""
https://leetcode.com/problems/reorganize-string/description/

Given a string s, rearrange the characters of s so that any two adjacent characters are not the same.

Return any possible rearrangement of s or return "" if not possible.

 

Example 1:

Input: s = "aab"
Output: "aba"
Example 2:

Input: s = "aaab"
Output: ""


"""
class Solution:
    def reorganizeString(self, s: str) -> str:
        import heapq
        count = Counter(s)
        print(count)
        lst = [(-cnt,val) for val, cnt in count.items()]
        heapq.heapify(lst)
        next = None
        out = ""
        # the idea is to burnout the higest duplicate elements before using unique elements.
        # always take element which has more duplicate 
        # next will hold previous element and healify ensures always element with highest duplicate value will come
        #using next we always take altenative element between 1st highest and 2nd highest duplicate elements.
        while len(lst) or next:
            cnt, val = heapq.heappop(lst)
            print(cnt, val)
            if cnt<-1 and len(lst)==0 and next == None:
                return ""
            out+=val
            cnt+=1
            if next:
                heapq.heappush(lst,next)
                next = None
            if cnt<0:
                next = (cnt, val)
        return out

        

        
