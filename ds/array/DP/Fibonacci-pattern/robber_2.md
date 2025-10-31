```
https://leetcode.com/problems/house-robber-iii/description/?envType=problem-list-v2&envId=dynamic-programming


The thief has found himself a new place for his thievery again. There is only one entrance to this area, called root.
Besides the root, each house has one and only one parent house. After a tour, the smart thief realized that all houses 
in this place form a binary tree. It will automatically contact the police if two directly-linked houses were broken into on the same night.

Given the root of the binary tree, return the maximum amount of money the thief can rob without alerting the police.

Note:
sol1: take two value for each node  (with root, without root), then for each parent calculate [with root + left value without left root + right value without right root], without root , max of left value and right value.
sol2:
( this solution will not work always) convert a layer of nodes to single value. then the tree will become a array.
constraint is two direfclty linked houses can 't be theft, i.e after robbed parent we can't theft child. hence thief can robb one level (bfs).
```
<img width="685" height="842" alt="image" src="https://github.com/user-attachments/assets/216459d9-a0fd-407a-9025-e9029a554695" />

``` python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    """
    Input: [3,4,5,1,3,null,1]
 input tree            dp tree:
     3                  [3+3+1,4+5]
    / \                /        \
   4   5            [4,3]      [5,1]
  / \   \          /     \          \
 1   2   1      [1,0]    [2,0]     [1,0]
                / \       /  \        /  \
           [0,0] [0,0] [0,0] [0,0]  [0,0] [0,0]
    
    """
    def rob(self, root: TreeNode) -> int:
        return max(self.dfs(root))
    
    def dfs(self, root: TreeNode):
        if not root:
            # (with adding root, without adding root)
            return (0, 0)
        left = self.dfs(root.left)
        right = self.dfs(root.right)
        return (root.val + left[1] + right[1], max(left[0], left[1]) + max(right[0], right[1]))
        #.     ^ root + left side without root + right side without root ( if i am taking root then i can take all the below value except its immediate chield)
        #                                        ^ max left (with root , without root) + maxright (with root, without root). if i am not taking root, then i am free to take left side with root or withour root value.



```
``` python

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def rob(self, root: Optional[TreeNode]) -> int:
        # note: convert a layer of nodes to single value. then the tree will become a array.
        arr = []
        dfs = []
        dfs.append(root)
        l=0
        while 1==1:
            sm = 0
            tl=len(dfs)
            for i in range(l, len(dfs)):
                node = dfs[i]
                sm += node.val
                if node.left != None:
                    dfs.append(node.left)
                if node.right != None:
                    dfs.append(node.right)
            l=tl
            arr.append(sm)
            if tl == len(dfs):
                break
            
        print(arr)
        # now apply simple roborry problem 
        for i in range(1,len(arr)):
            if i ==1:
                arr[i] = max(arr[i], arr[i-1] )
            else:
                arr[i] = max(arr[i]+arr[i-2], arr[i-1] )
        return arr[-1]
```

