```

https://leetcode.com/problems/min-stack/



Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.

Implement the MinStack class:

MinStack() initializes the stack object.
void push(int val) pushes the element val onto the stack.
void pop() removes the element on the top of the stack.
int top() gets the top element of the stack.
int getMin() retrieves the minimum element in the stack.
You must implement a solution with O(1) time complexity for each function.

 

Example 1:

Input
["MinStack","push","push","push","getMin","pop","top","getMin"]
[[],[-2],[0],[-3],[],[],[],[]]

Output
[null,null,null,null,-3,null,0,-2]

Explanation
MinStack minStack = new MinStack();
minStack.push(-2);
minStack.push(0);
minStack.push(-3);
minStack.getMin(); // return -3
minStack.pop();
minStack.top();    // return 0
minStack.getMin(); // return -2

Note:

    
```


``` python

class MinStack:

    def __init__(self):
        self.stk = []
        

    def push(self, val: int) -> None:
        if len(self.stk) == 0:
            self.stk.append([val, val])
        else:
            if self.stk[-1][1] > val:
                self.stk.append([val,val])
            else:
                self.stk.append([val, self.stk[-1][1]])
        

    def pop(self) -> None:
        del self.stk[-1]
        

    def top(self) -> int:
        return self.stk[-1][0] if self.stk else None

    def getMin(self) -> int:
        return self.stk[-1][1] if self.stk else None


# Your MinStack object will be instantiated and called as such:
# obj = MinStack()
# obj.push(val)
# obj.pop()
# param_3 = obj.top()
# param_4 = obj.getMin()

```
