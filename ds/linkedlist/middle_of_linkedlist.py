# find the middle of linkedlist with minimum time complexity

class linkedlist:
    def __init__(self, value, next):
        self.value = value
        self.next = next

def mid_linkedlist(head):
    p1 = head
    p2 = head
    while p2 != None:
        if p2.next == None:
            break
        p1=p1.next
        p2=p2.next.next
    print(p1.value)

n0 = linkedlist(9,None)
n1 = linkedlist(8,n0)
n2 = linkedlist(7,n1)
n3 = linkedlist(6,n2)
n4 = linkedlist(5,n3)
n5 = linkedlist(4,n4)
n6 = linkedlist(3,n5)
n7 = linkedlist(2,n6)
head = linkedlist(1,n7)
mid_linkedlist(head)
