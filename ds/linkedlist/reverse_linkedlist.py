""""
reverse linked list
"""
class linkedlist:
    def __init__(self, val, nxt):
        self.val = val
        self.next = nxt
def reverse_linkedin_list(head):
    p1 = head
    if p1.next == None:
        return head
    if p1.next.next == None:
        p2 = p1.next
        p2.next = p1
        p1.next = None
        return p1
    p2 = p1.next
    p3 = p2.next
    while p3 != None:
        p2.next = p1
        p1= p2
        p2 = p3
        p3 = p3.next
    head.next = None
    p2.next = p1
    head = p2
    return head

def printlinkedlist(head):
    while head !=None:
        print(head.val)
        head = head.next
h6 = linkedlist(1, None)
h5 = linkedlist(2, h6)
h4 = linkedlist(3, h5)
h3 = linkedlist(4, h4)
h2 = linkedlist(5, h3)
h1 = linkedlist(6, h2)
h = linkedlist(7, h1)
printlinkedlist(reverse_linkedin_list(h))
