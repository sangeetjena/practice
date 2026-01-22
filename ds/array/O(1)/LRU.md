```
https://leetcode.com/problems/lru-cache/description/



Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the LRUCache class:

LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
int get(int key) Return the value of the key if the key exists, otherwise return -1.
void put(int key, int value) Update the value of the key if the key exists. Otherwise, add the key-value pair to the cache. If the number of keys exceeds the capacity from this operation, evict the least recently used key.
The functions get and put must each run in O(1) average time complexity.

 

Example 1:

Input
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
Output
[null, null, null, 1, null, -1, null, -1, 3, 4]

Explanation
LRUCache lRUCache = new LRUCache(2);
lRUCache.put(1, 1); // cache is {1=1}
lRUCache.put(2, 2); // cache is {1=1, 2=2}
lRUCache.get(1);    // return 1
lRUCache.put(3, 3); // LRU key was 2, evicts key 2, cache is {1=1, 3=3}
lRUCache.get(2);    // returns -1 (not found)
lRUCache.put(4, 4); // LRU key was 1, evicts key 1, cache is {4=4, 3=3}
lRUCache.get(1);    // return -1 (not found)
lRUCache.get(3);    // return 3
lRUCache.get(4);    // return 4


Note: 1- take dictionary for O(1) search
      2- take double linked list to add or remove the element if it is our of boundary.



```


``` python

class Node:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None
class LRUCache:
    # use a hash table and a double linked list 
    # hash table will alwasys tell if the element exists in teh cache in O(1) and double linked list 
    # insert the element and remove last element (in case of overflow) in O(1) time complexity.
 
    def __init__(self, capacity: int):
        
        self.capacity = capacity
        self.count = 0
        self.map = {}
        self.head = None
        self.tail = None

    def get(self, key: int) -> int:
        
        if self.map.get(key, None) != None:
            temp = self.map[key][1]
            print(temp, self.head)
            if temp == self.tail:
                return self.map[key][0]
            if temp == self.head:
                self.head = self.head.next
                self.head.prev = None
            else:
                temp.prev.next = temp.next
                temp.next.prev = temp.prev
            temp.next = None
            temp.prev = self.tail
            self.tail.next = temp
            self.tail = self.tail.next
            return self.map[key][0]
        return -1
        
        
    def put(self, key: int, value: int) -> None:
        
        if self.map.get(key, None) == None:
            node = Node(key)
            self.count+=1
            self.map[key] = [value, node]
            if self.head == None:
                self.head = node
                self.tail = node
            else:
                self.tail.next = node
                node.prev = self.tail
                self.tail = node
        else:
            self.map[key][0] = value
            temp = self.map[key][1]
            if temp == self.tail:
                return self.map[key][0]
            if temp == self.head:
                self.head = self.head.next
                self.head.prev = None
            else:
                temp.prev.next = temp.next
                temp.next.prev = temp.prev
            temp.next = None
            temp.prev = self.tail
            self.tail.next = temp
            self.tail = self.tail.next

        if self.count> self.capacity:
            self.count-=1
            del self.map[self.head.val]
            self.head = self.head.next
            if self.head:
                self.head.prev.next = None
                self.head.prev = None
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)

```
