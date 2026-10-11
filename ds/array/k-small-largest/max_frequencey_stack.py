"""
https://leetcode.com/problems/maximum-frequency-stack/description/

Design a stack-like data structure to push elements to the stack and pop the most frequent element from the stack.

Implement the FreqStack class:

FreqStack() constructs an empty frequency stack.
void push(int val) pushes an integer val onto the top of the stack.
int pop() removes and returns the most frequent element in the stack.
If there is a tie for the most frequent element, the element closest to the stack's top is removed and returned.
 

Example 1:

Input
["FreqStack", "push", "push", "push", "push", "push", "push", "pop", "pop", "pop", "pop"]
[[], [5], [7], [5], [7], [4], [5], [], [], [], []]
Output
[null, null, null, null, null, null, null, 5, 7, 5, 4]

Explanation
FreqStack freqStack = new FreqStack();
freqStack.push(5); // The stack is [5]
freqStack.push(7); // The stack is [5,7]
freqStack.push(5); // The stack is [5,7,5]
freqStack.push(7); // The stack is [5,7,5,7]
freqStack.push(4); // The stack is [5,7,5,7,4]
freqStack.push(5); // The stack is [5,7,5,7,4,5]
freqStack.pop();   // return 5, as 5 is the most frequent. The stack becomes [5,7,5,7,4].
freqStack.pop();   // return 7, as 5 and 7 is the most frequent, but 7 is closest to the top. The stack becomes [5,7,5,4].
freqStack.pop();   // return 5, as 5 is the most frequent. The stack becomes [5,7,4].
freqStack.pop();   // return 4, as 4, 5 and 7 is the most frequent, but 4 is closest to the top. The stack becomes [5,7].
"""

class FreqStack:

    def __init__(self):
        self.dict = defaultdict(lambda : {'freq': int(), 'i': list()})
        self.heap = []
        self.ind = -1
        
    def push(self, val: int) -> None:
        self.ind+=1
        self.dict[val]['freq']+=1
        if self.dict[val]['i'] is None:
            self.dict[val]['i'] = [self.ind*-1]
        else:
            self.dict[val]['i'].append(self.ind*-1)
        self.heap = []
        for k in self.dict.keys():
            heapq.heappush(self.heap, (self.dict[k]['freq']*-1, sorted(self.dict[k]['i']), k))

    def pop(self) -> int:
        if not self.heap:
            return []
        f,i,k = heapq.heappop(self.heap)
        self.dict[k]['freq']-=1
        del self.dict[k]['i'][-1]
        if -f>1:
            heapq.heappush(self.heap, (f+1,i[1:], k))
        else:
            del self.dict[k]
        return k



# Your FreqStack object will be instantiated and called as such:
# obj = FreqStack()
# obj.push(val)
# param_2 = obj.pop()
