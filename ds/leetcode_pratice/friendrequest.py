"""There are n persons on a social media website. You are given an integer array ages where ages[i] is the age of the ith person.

A Person x will not send a friend request to a person y (x != y) if any of the following conditions is true:

age[y] <= 0.5 * age[x] + 7
age[y] > age[x]
age[y] > 100 && age[x] < 100
Otherwise, x will send a friend request to y.

Note that if x sends a request to y, y will not necessarily send a request to x. Also, a person will not send a friend request to themself.

Return the total number of friend requests made.



Example 1:

Input: ages = [16,16]
Output: 2
Explanation: 2 people friend request each other.
Example 2:

Input: ages = [16,17,18]
Output: 2
Explanation: Friend requests are made 17 -> 16, 18 -> 17.
"""

class Solution:
    def maxFriendRequest(self, arr):
        countfriendrequest = 0
        for y in range(len(arr)):
            for x in range(len(arr)):
                if arr[y] <= (arr[x] * 0.5 + 7) or arr[y] > arr[x] or (arr[y] > 100 and arr[x]<100) or x==y:
                    continue
                else:
                    countfriendrequest += 1
        print(countfriendrequest)

obj = Solution()
obj.maxFriendRequest([20,30,100,110,120])