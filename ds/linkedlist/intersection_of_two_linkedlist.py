"""
https://leetcode.com/problems/intersection-of-two-linked-lists/description/

Given the heads of two singly linked-lists headA and headB, return the node at which the two lists intersect. If the two linked lists have no intersection at all, return null.

For example, the following two linked lists begin to intersect at node c1:


The test cases are generated such that there are no cycles anywhere in the entire linked structure.

Note that the linked lists must retain their original structure after the function returns.

Custom Judge:

The inputs to the judge are given as follows (your program is not given these inputs):

intersectVal - The value of the node where the intersection occurs. This is 0 if there is no intersected node.
listA - The first linked list.
listB - The second linked list.
skipA - The number of nodes to skip ahead in listA (starting from the head) to get to the intersected node.
skipB - The number of nodes to skip ahead in listB (starting from the head) to get to the intersected node.
The judge will then create the linked structure based on these inputs and pass the two heads, headA and headB to your program. If you correctly return the intersected node, then your solution will be accepted.

Note:
approach 1: create a dictionary and move two head of linkedlist one after other. if address is already visited then found the intersection point
approach 2: find the length of two linked list and find the difference and forward the head for the linkedlist whose length is larger. then move two head in parallel. and two
pointer will meet at the same time.

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

            
