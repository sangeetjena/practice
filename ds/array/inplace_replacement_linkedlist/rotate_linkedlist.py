"""

https://leetcode.com/problems/rotate-list/solutions/4294994/beats-97-of-user-python-easy-solution-explained/

"""

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution(object):
    def rotateRight(self, head, k):
        if head == None or head.next == None :
            return head
        length=1
        end = head
        while end.next!=None:
            length += 1
            end = end.next
        print(length, k%length)
        if (  k% length == 0):
            return head
        # if k is greter than length of linked list then we need to substract all full rotation and remaining would be the actual rotation needed.
        pos= length - (k%length)
        count = 1
        prev = curr = head
        # cut the range and place it in the starting position of the linkedlist
        while True:
            if count < pos:
                prev = prev.next
                count+=1
                continue
            curr = prev.next
            prev.next = end.next
            end.next = head
            head = curr
            break
        return head
            


        
