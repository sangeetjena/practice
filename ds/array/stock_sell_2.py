class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        maxVal = 0
        tendMax = 0
        prevValue = prices[0]
        startTrendValue = -1
        for i in range(1, len(prices)):
            if prices[i] > prevValue:
                if startTrendValue == -1:
                    startTrendValue = prevValue
                prevValue = prices[i]
                continue
            else:
                if startTrendValue == -1:
                    prevValue = prices[i]
                    continue
                print("trend start=  {} and end at {}".format(startTrendValue, prevValue))
                maxVal += (prevValue - startTrendValue)
                prevValue = prices[i]
                startTrendValue = -1
        if startTrendValue > -1:
            maxVal += (prevValue - startTrendValue)
        return maxVal




