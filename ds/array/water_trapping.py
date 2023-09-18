
"""
solution is : at each point, look for it max wall in left and max wall at right.
then find the min between those two wall.
maximum hight of water can collect at that point is min height of (left wall, righ wall)
then find the water level = water level at that point - height of building
then sum all water levels in each building.
"""
def find_max_water(arr):
    max_left = [0 for i in range(len(arr))]
    max_right = [0 for i in range(len(arr))]
    max_left[0] = arr[0]
    max_right[-1] = arr[-1]
    sum = 0
    for i in range(1,len(arr)):
        max_left[i] = max(arr[i], max_left[i-1])
        max_right[len(arr)-1-i] = max(arr[len(arr)-1-i], max_right[len(arr)-i])
    print(max_left, max_right)
    for i in range(len(arr)):
        sum+= min(max_left[i],max_right[i]) - arr[i]
    return sum

arr = [3,1,2,4,0,1,3,2]
print(find_max_water(arr))