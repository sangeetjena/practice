"""
https://leetcode.com/problems/linked-list-cycle-ii/submissions/1283344582/
https://www.youtube.com/watch?v=95ZfuoSAUPI


NOte:take one slow and fast pointer where it will meet that is the start point of cycle
"""
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = fast = head
        while fast!=None and fast.next!=None:
            fast=fast.next.next
            slow = slow.next

            if fast == slow:
                cnt=0
                while slow != head:
                    slow = slow.next
                    head = head.next
                    cnt+=1
                return head
        return None
        
