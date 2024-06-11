"""
https://leetcode.com/problems/reorder-list/

"""
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        """
        Do not return anything, modify head in-place instead.
        """
        fast = slow = head
        while fast and fast.next:
            fast=fast.next.next
            slow= slow.next
        # reverse from slow pointer
        prev = None
        while slow:
            temp = slow.next
            slow.next = prev
            prev = slow
            slow = temp
        p1 = head
        while p1 and prev:
            temp1 = prev.next
            temp2 = p1.next
            p1.next = prev
            # in the reversal we had not make the end node of the 1st half lineked list to null
            # so circle linkedinlist exist. this is to make the last node null.
            if temp2 != prev:
                prev.next = temp2
            else:
                prev.next = None
            p1 = temp2
            prev = temp1
        
        
