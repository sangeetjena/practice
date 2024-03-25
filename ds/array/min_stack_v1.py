

class min_stack:
    stck = []
    min_stck = []
    def push(self, x):
        if len(self.min_stck) == 0 or self.min_stck[-1] > x:
            self.min_stck.append(x)
            self.stck.append(x)
        else:
            self.min_stck.append(self.min_stck[-1])
            self.stck.append(x)
    def pop(self):
        min = self.min_stck[-1]
        del self.min_stck[-1]
        del self.stck[-1]
        return min
    def get_min(self):
        return self.min_stck[-1]


obj = min_stack()
obj.push(6)
obj.push(10)
obj.push(8)
obj.push(3)
obj.push(7)
obj.pop()
obj.pop()
print(obj.get_min())
