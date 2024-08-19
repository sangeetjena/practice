"""
https://leetcode.com/problems/merge-k-sorted-lists/description/

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.

Merge all the linked-lists into one sorted linked-list and return it.

 

Example 1:

Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
Explanation: The linked-lists are:
[
  1->4->5,
  1->3->4,
  2->6
]
merging them into one sorted list:
1->1->2->3->4->4->5->6

"""
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        out = []
        heap = []
        dummynode = ListNode()
        head = dummynode
        # take all 1st elements in the linkedlist and create a heap.
        for i,node in enumerate(lists):
            if node:
                heapq.heappush(heap,(node.val,i, node))
        while len(heap)>0:
            # extract mean heap and push the next value of the extracted node back to heap
            elem,i, node = heapq.heappop(heap)
            head.next = node
            head=node
            node = node.next
            if node:
                heapq.heappush(heap,(node.val,i, node))
        return dummynode.next

        
        
