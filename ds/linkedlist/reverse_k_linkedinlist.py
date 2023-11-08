"""
reverse linkedlist in a group of k
in k group 1st elemnt will point to next group
and last element will become head
"""
class linkedlist:
    def __init__(self, val, nxt):
        self.val = val
        self.next = nxt

def reversed_k_linkedlist(head,k):
    if k == 1:
        return head
    if head == None:
        return None
    # if only 1 nodes are there
    if head.next == None:
        return head
    p1 = head
    p2 = p1.next
    # if only 2 nodes are there
    if p2.next == None:
        p2.next = p1
        p1.next = None
        return p2
    p3 = p2.next
    temphead = p1
    for i in range(1,k-1):
        if p3 is None:
            break
        p2.next = p1
        p1 = p2
        p2 = p3
        p3 = p3.next
    p2.next = p1
    temphead.next = reversed_k_linkedlist(p3,k)
    return p2

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
printlinkedlist(reversed_k_linkedlist(h,2))
