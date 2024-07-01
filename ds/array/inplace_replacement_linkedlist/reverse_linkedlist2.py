"""
https://leetcode.com/problems/reverse-linked-list-ii/
https://www.youtube.com/watch?v=RF_M9tX4Eag
"""
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        if head.next == None:
            return head
        # to handle the case if replacement start from the begining of the linked list
        tempnode = ListNode(0,head)
        head = tempnode
        tempprev , curr , nxt = head, head, head
        prev = None
        # as i have added a dummy node
        count=-1
        while count< right:
            nxt = curr.next
            count +=1
            if count < left:
                print("enter")
                tempprev = curr
                curr = curr.next 
                continue
            curr.next = prev
            prev = curr
            curr=nxt
        tempprev.next.next = nxt
        tempprev.next = prev
        return head.next
            

        
