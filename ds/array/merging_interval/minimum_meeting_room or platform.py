"""
""https://www.geeksforgeeks.org/problems/minimum-platforms-1587115620/1"

"""


class Solution:    
    #Function to find the minimum number of platforms required at the
    #railway station such that no train waits.
    def minimumPlatform(self,n,arr,dep):
        # code here
        arr.sort()
        dep.sort()
        s=e=tcount=count=0
        while s< n and e<n:
            if arr[s]<dep[e]:
                tcount+=1
                s+=1
            else:
                tcount-=1
                e+=1
            count=max(count, tcount)
        return count
