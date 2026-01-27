```
https://leetcode.com/problems/all-oone-data-structure/description/


Design a data structure to store the strings' count with the ability to return the strings with minimum and maximum counts.

Implement the AllOne class:

AllOne() Initializes the object of the data structure.
inc(String key) Increments the count of the string key by 1. If key does not exist in the data structure, insert it with count 1.
dec(String key) Decrements the count of the string key by 1. If the count of key is 0 after the decrement, remove it from the data structure. It is guaranteed that key exists in the data structure before the decrement.
getMaxKey() Returns one of the keys with the maximal count. If no element exists, return an empty string "".
getMinKey() Returns one of the keys with the minimum count. If no element exists, return an empty string "".
Note that each function must run in O(1) average time complexity.

 

Example 1:

Input
["AllOne", "inc", "inc", "getMaxKey", "getMinKey", "inc", "getMaxKey", "getMinKey"]
[[], ["hello"], ["hello"], [], [], ["leet"], [], []]
Output
[null, null, null, "hello", "hello", null, "hello", "leet"]

Explanation
AllOne allOne = new AllOne();
allOne.inc("hello");
allOne.inc("hello");
allOne.getMaxKey(); // return "hello"
allOne.getMinKey(); // return "hello"
allOne.inc("leet");
allOne.getMaxKey(); // return "hello"
allOne.getMinKey(); // return "leet"


Note:
  1- use dictionary to keep the address of the key in the linked list
  2- use double linkedlist to keep freqenecy in sorted way, where head is min and tail is the max  frequency.

```


``` python

class Node:
    def __init__(self, freq):
        self.freq = freq
        self.value = set()
        self.prev = None
        self.next = None


class AllOne:

    def __init__(self):
        self.map = {}      # key -> Node
        self.head = None
        self.end = None

    def _remove_node(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.end = node.prev

        node.prev = None
        node.next = None

    def incrementOrDecrementNode(self, key, freq, inc):

        if inc:
            # ---------------- INC ----------------
            if key not in self.map:
                # new key, freq = 1
                if not self.head or self.head.freq != 1:
                    node = Node(1)
                    node.value.add(key)
                    node.next = self.head
                    if self.head:
                        self.head.prev = node
                    self.head = node
                    if not self.end:
                        self.end = node
                else:
                    self.head.value.add(key)
                    node = self.head

                self.map[key] = node

            else:
                curr = self.map[key]
                next_freq = curr.freq + 1

                if curr.next and curr.next.freq == next_freq:
                    nxt = curr.next
                else:
                    nxt = Node(next_freq)
                    nxt.next = curr.next
                    nxt.prev = curr
                    if curr.next:
                        curr.next.prev = nxt
                    curr.next = nxt
                    if curr == self.end:
                        self.end = nxt

                nxt.value.add(key)
                self.map[key] = nxt
                curr.value.remove(key)

                if not curr.value:
                    self._remove_node(curr)

        else:
            # ---------------- DEC ----------------
            curr = self.map[key]

            if curr.freq == 1:
                del self.map[key]
                curr.value.remove(key)
                if not curr.value:
                    self._remove_node(curr)
                return

            prev_freq = curr.freq - 1

            if curr.prev and curr.prev.freq == prev_freq:
                prv = curr.prev
            else:
                prv = Node(prev_freq)
                prv.prev = curr.prev
                prv.next = curr
                if curr.prev:
                    curr.prev.next = prv
                curr.prev = prv
                if curr == self.head:
                    self.head = prv

            prv.value.add(key)
            self.map[key] = prv
            curr.value.remove(key)

            if not curr.value:
                self._remove_node(curr)

    def inc(self, key: str) -> None:
        self.incrementOrDecrementNode(key, None, True)

    def dec(self, key: str) -> None:
        if key in self.map:
            self.incrementOrDecrementNode(key, None, False)

    def getMaxKey(self) -> str:
        if not self.end:
            return ""
        return next(iter(self.end.value))

    def getMinKey(self) -> str:
        if not self.head:
            return ""
        return next(iter(self.head.value))


```
