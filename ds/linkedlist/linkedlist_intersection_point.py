"""
https://leetcode.com/problems/intersection-of-two-linked-lists/description/

Note: simply increment the pointer of the longest linkedlist by its difference of length with smaller list, and start comparing two pointer
"""
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def findLen(self,head:ListNode):
        cnt = 0 
        while head:
            cnt+=1
            head=head.next
        return cnt


    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> Optional[ListNode]:
        prev = None
        if headA == None or headB == None:
            return None
        lenA,lenB = 1,1
        if headA.next:
            lenA = self.findLen(headA)
        if headB.next:
            lenB = self.findLen(headB)
        diff = abs(lenA - lenB)
        for i in range(diff):
            if lenA> lenB:
                headA = headA.next
            else:
                headB = headB.next
        while headA:
            if headA == headB:
                return headA
            headA = headA.next
            headB = headB.next
        return None

            
