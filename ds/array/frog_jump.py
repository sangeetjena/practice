"""
A frog is crossing a river. The river is divided into some number of units, and at each unit, there may or may not exist a stone. The frog can jump on a stone, but it must not jump into the water.

Given a list of stones positions (in units) in sorted ascending order, determine if the frog can cross the river by landing on the last stone. Initially, the frog is on the first stone and assumes the first jump must be 1 unit.

If the frog's last jump was k units, its next jump must be either k - 1, k, or k + 1 units. The frog can only jump in the forward direction.

Example 1:

Input: stones = [0,1,3,5,6,8,12,17]
Output: true
Explanation: The frog can jump to the last stone by jumping 1 unit to the 2nd stone, then 2 units to the 3rd stone, then 2 units to the 4th stone, then 3 units to the 6th stone, 4 units to the 7th stone, and 5 units to the 8th stone.
"""
def frog_jump(arr):
    dp = {x:[] for x in arr}
    dp[arr[0]].append(0)
    for x in arr:
        for i in dp[x]:
            k1= i -1
            k2 = i
            k3 = i+1
            if k1 > 0 and x + k1 in arr:
                dp[x + k1].append(k1)
            if k2 > 0 and x + k2 in arr:
                dp[x + k2].append(k2)
            if k3 > 0 and x + k3 in arr:
                dp[x + k3].append(k3)
    print(dp)
    if(dp[arr[-1]].__len__()>0):
        return True
    else:
        return False


stones = [0,1,3,5,6,8,12,17]
print(frog_jump(stones))

stones = [0,1,2,3,4,8,9,11]

print(frog_jump(stones))