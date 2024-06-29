"""
https://github.com/Chanda-Abdul/Several-Coding-Patterns-for-Solving-Data-Structures-and-Algorithms-Problems-during-Interviews/blob/main/%E2%9C%85%20%20Pattern%2006%3A%20In-place%20Reversal%20of%20a%20LinkedList.md
https://leetcode.com/problems/reverse-linked-list/
"""
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head == None:
            return head
        p1=None
        p2= head
        p3=head
        while(p3 != None):
            p3= p2.next
            p2.next = p1
            p1=p2
            p2=p3
        return p1
        
