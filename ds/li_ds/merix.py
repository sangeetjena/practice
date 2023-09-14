"""
DWH CA Question: Write an algorithm such that if an element in an MxN matrix is 0, its entire row and column are set to 0.
Example:

[ 1, 1, 1

  0, 1, 1

  0, 0, 1]

In this example, first column has element 0, so all the elements in the first column have to be made 0. Second row and third row have 0 elements, so all the elements in those rows have to be made 0.

Output matrix:

[ 0, 0, 1

  0, 0, 0

  0, 0, 0]
"""
def  metrix(arr):
    print(arr)
    lst = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i][j] == 0:
                lst.append((i,j))
    for x in lst:
        i,j = x
        for k in  range(len(arr)):
            arr[i][k] = 0
            arr[k][j] = 0
    return arr
print(metrix([[ 1, 1, 1],[0, 1, 1],[0, 0, 1]]))