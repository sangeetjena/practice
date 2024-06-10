"""

https://leetcode.com/problems/middle-of-the-linked-list/
"""

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        fast=slow=head
        cnt=0
        while fast!=None and fast.next!=None:
            fast = fast.next.next
            slow = slow.next
            cnt+=1
        
        return slow
