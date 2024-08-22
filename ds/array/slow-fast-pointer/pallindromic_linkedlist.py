"""
https://leetcode.com/problems/palindrome-linked-list/
https://www.youtube.com/watch?v=yOzXms1J6Nk
# reach to the half of the linked list  and second half linked list reverse it then check two linkedin list if same or not.
"""

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        fast = slow = head
        while fast!=None and fast.next!=None:
            fast=fast.next.next
            slow=slow.next
        prev = None
        while slow:
            temp = slow.next
            slow.next = prev
            prev = slow
            slow = temp
        while prev:
            if head.val != prev.val:
                return False
            prev=prev.next
            head=head.next
        return True
        
