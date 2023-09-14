def max_floor_unbroken_egg(arr, no_egg,tot_floor, curr_floor ):
    if no_egg == 0:
        return 0
    if curr_floor == 0 or curr_floor == 1:
        return curr_floor
    for i in range(tot_floor):


