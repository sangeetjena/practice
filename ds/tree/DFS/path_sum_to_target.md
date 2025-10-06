```
https://leetcode.com/problems/path-sum-iii/description/

Note: similar to prefix sum ( sub array sum to target)
go down to the childs and keep adding to the total sum . and check if any prefix sum found.
at the time of returning to the parent substract the child value from the prefix sum.
```

<img width="657" height="606" alt="image" src="https://github.com/user-attachments/assets/2611652b-1eff-485b-8f57-f1b02c30aa5a" />

```python
# optimal solution using prefix sum:
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        # Note: THis is similar to the prefix sum problem. but in tree. 
        # the total sum will increase when traversal is in one direction, when it change the direction then, reset the sum again and cntinue. 
        self.totalMatch = 0
        from collections import defaultdict
        def findTarget(root, total, prefixSum):
            if root == None:
                return
            if (total+root.val) - targetSum in prefixSum.keys():
                self.totalMatch+=prefixSum[(total+root.val)-targetSum]
                print("found one" + str(self.totalMatch))
            # add value to the prefix sum
            prefixSum[total + root.val]+=1
            findTarget(root.left,total+root.val, prefixSum)
            findTarget(root.right, total+root.val, prefixSum)
            # during back tracking remove the value from the prefix sum.
            prefixSum[total + root.val]-=1
        findTarget(root, 0, defaultdict(int, {0:1}))
        return self.totalMatch
        
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        if root is None:
            return 0
        prefix_sum = {0:1}
        dfs = []
        visited = []
        total = 0
        count = 0
        dfs.append(root)
        while len(dfs)>0:
            node = dfs[-1]
            # if already visited then remove it one count value from prfix sum and remove from dfs.
            if node in visited:
                prefix_sum[total]-=1
                total-=node.val
                del dfs[-1]
                continue
            total += node.val
            if total -  targetSum  in prefix_sum.keys():
                # count = existing count + reminder count
                count+= prefix_sum[total -  targetSum]
            # increment total value index by one 
            prefix_sum[total] = prefix_sum.get(total,0) + 1
            if node.left:
                dfs.append(node.left)
            if node.right:
                dfs.append(node.right)
            visited.append(node)
        return count
```

