"""
https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/description/?envType=problem-list-v2&envId=two-pointers
https://www.youtube.com/watch?v=eFPFwwojxGU

Given the head of a sorted linked list, delete all nodes that have duplicate numbers, leaving only distinct numbers from the original list. Return the linked list sorted as well.

 

Example 1:


Input: head = [1,2,3,3,4,4,5]
Output: [1,2,5]

Note: use dummy node and assign prev = dummy. then if i find duplicate then move curr only and at first instance when curr.val != curr.next.val then assign prev.next and move curr
on the next iteration if still curr.val and curr.next.val is unique then move prev to curr and move curr to curr next.
"""
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head == None:
            return head
        dummy = ListNode()
        dummy.next = head
        prev = dummy
        curr = head
        # curr and curr.next to avoid out of bondary case
        while curr and curr.next:
            if curr.val == curr.next.val:
                while curr.next and curr.val == curr.next.val:
                    curr = curr.next
                # have not move the prev pointer, only setting prev.next to curr.next
                # if in next iteration curr and curr.next is non duplicate value then only prev will move to next value.
                prev.next = curr.next
                curr = curr.next
            else:
                prev = curr
                curr = curr.next
        return dummy.next
