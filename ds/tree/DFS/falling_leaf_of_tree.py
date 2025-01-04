"""
https://leetcode.com/problems/find-leaves-of-binary-tree/description/?envType=company&envId=linkedin&favoriteSlug=linkedin-thirty-days

Given the root of a binary tree, collect a tree's nodes as if you were doing this:

Collect all the leaf nodes.
Remove all the leaf nodes.
Repeat until the tree is empty.
 

Example 1:


Input: root = [1,2,3,4,5]
Output: [[4,5,3],[2],[1]]
Explanation:
[[3,5,4],[2],[1]] and [[3,4,5],[2],[1]] are also considered correct answers since per each level it does not matter the order on which elements are returned.

# Note: print level in the reverse order. i.e from leaf to the root node.
# the idea is to use dfs and assing level for the reverse traversal. in the dfs once we reached to the leaf node it level will be 0. and during back tracking its  parent nodes will become its child level +1.
# then asssing elements to the list with the index as level value.
"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def findLeaves(self, root: Optional[TreeNode]) -> List[List[int]]:
        # the idea is to use dfs and assing level for the reverse traversal. in the dfs once we reached to the leaf node it level will be 0. and during back tracking its  parent nodes will become its child level +1.
        # then asssing elements to the list with the index as level value.
        # Note: print level in the reverse order. i.e from leaf to the root node.
        finalresult = DefaultDict(list)
        def dfs(root):
            if root == None:
                return 0
            left = dfs(root.left)
            right = dfs(root.right)
            level = max(left,right)
            finalresult[level].append(root.val)
            return level+1
        dfs(root)
        
        # print(([finalresult[i] for i in sorted(finalresult.keys())]))
        return [finalresult[i] for i in sorted(finalresult.keys())]



        
