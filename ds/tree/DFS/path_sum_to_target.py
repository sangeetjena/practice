"""
https://leetcode.com/problems/path-sum-iii/description/

Note: similar to prefix sum ( sub array sum to target)
"""
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
            prefixSum[total + root.val]+=1
            findTarget(root.left,total+root.val, prefixSum)
            findTarget(root.right, total+root.val, prefixSum)
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


