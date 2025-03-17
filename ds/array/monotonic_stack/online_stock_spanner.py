"""
https://leetcode.com/problems/online-stock-span/description/?envType=study-plan-v2&envId=leetcode-75

Note: monotonic stack pattern. when find a value greater than the values in teh stack evalute all the value and 
insert the new value along with total count because of new value.

"""

class StockSpanner:

    def __init__(self):
        self.stack = []
        

    def next(self, price: int) -> int:
        count = 1
        while len(self.stack)>0 and self.stack[-1][0] <= price:
            count+=self.stack[-1][1]
            del self.stack[-1]
        self.stack.append((price,count))
        return count


        


# Your StockSpanner object will be instantiated and called as such:
# obj = StockSpanner()
# param_1 = obj.next(price)
