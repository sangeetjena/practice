"""
find min stack with O(1) operation.
ref:  https://www.youtube.com/watch?v=QMlDCR9xyd8
"""
class min_stack:
    def __init__(self):
        self.min =0
        self.stack = []
    def push(self, val):
        if self.stack.__len__() == 0:
            self.min = val
        if self.min > val:
            self.stack.append(2 * val - self.min)
            self.min = val
        else:
            self.stack.append(val)
    def pop(self):
        val = self.stack[-1]
        if val < self.min:
            # if value in the stack is lesser than min then min is the holding the actual value.
            mn1 = self.min
            self.min = 2*self.min - val
            val = 2*self.min - val
            return mn1
        del self.stack[-1]
        return val
    def get_min(self):
        return self.min

obj = min_stack()
obj.push(6)
obj.push(10)
obj.push(8)
obj.push(3)
obj.push(7)
obj.pop()
obj.pop()
print(obj.get_min())


