class linkedlist:
    def __init__(self, val, next:None,):
        self.next = next
        self.val = val

def print_linked_list(head):
    while head.next != None:
        print(head.val)
        head = head.next

def sort_linked_list(head):
    dict = {0:0, 1:0,2:0}
    pointer = head
    while pointer.next != None:
        dict[pointer.val] +=1
        pointer = pointer.next
    pointer = head
    for i in range(0,3):
        for j in range(0, dict[i]):
            pointer.val = i
            pointer = pointer.next


n1 = linkedlist(0,None)
n2 = linkedlist(1,n1)
n3 = linkedlist(2,n2)
n4 = linkedlist(0,n3)
n5 = linkedlist(1,n4)
n6 = linkedlist(2,n5)
n7 = linkedlist(0,n6)
print_linked_list(n7)
sort_linked_list(n7)
print("----")
print_linked_list(n7)