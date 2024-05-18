"""
https://leetcode.com/problems/minimum-number-of-refueling-stops/description/
"""
class Solution:
    def minRefuelStops(self, target: int, startFuel: int, stations: List[List[int]]) -> int:
        # similar to frog jump problem
        if(len(stations)==0):
            if target> startFuel:
                return -1
            else:
                return 0
        dp = {stations[i][0]:[] for i in range(len(stations))}
        petrolpumpfuel = {stations[i][0]:stations[i][1] for i in range(len(stations))}
        dp[0] = [[0,startFuel]]
        petrolpumpfuel[0] = 0
        petrolpumpfuel[target] = 0
        dp[target] = []
        for key in sorted(dp.keys()):
            for cnt, carfuel in dp[key]:
                for key1 in sorted(dp.keys()):
                    if (key1 > key and key1<= key + carfuel):
                        dp[key1].append([cnt+1, (carfuel - (key1- key)) + petrolpumpfuel[key1]])
        print(dp)
        if len(dp[target]) == 0:
            return -1
        else:
            return min([lst[0] for lst in dp[target]])-1