import copy
def SubSetSum(arr, all_sets, pos, subsets, final):
    for i in range(pos, len(arr)):
        subsets.append(arr[i])
        SubSetSum(arr,all_sets,i+1, subsets, final)
        if(sum(subsets) == final):
            all_sets.append(copy.deepcopy(subsets))
        del(subsets[-1])
    return all_sets
arr = [3, 34, 4, 12, 5, 2]
res = SubSetSum(arr, [], 0, [], 13)
print(res)