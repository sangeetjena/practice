"""
https://leetcode.com/problems/find-duplicate-subtrees/description/
https://www.youtube.com/watch?v=kn0Z5_qPPzY

Given the root of a binary tree, return all duplicate subtrees.

For each kind of duplicate subtrees, you only need to return the root node of any one of them.

Two trees are duplicate if they have the same structure with the same node values.

Example 1:

Input: root = [1,2,3,4,null,2,4,null,null,4]
Output: [[2,4],[4]]

Note: in dfs find all sub tree serialization values and store it in hash map , then compare any sub stree seialize value matches or not.

"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def findDuplicateSubtrees(self, root: Optional[TreeNode]) -> List[Optional[TreeNode]]:
        subtree  = defaultdict(list)
        res = []
        def findSubtree(node):
            if node is None:
                return "null"
            s = ",".join([str(node.val), findSubtree(node.left), findSubtree(node.right)])
            # cheking if first time pattern find then capture it to result and rest duplicate values avoid, 
            # as it is expected in the result
            if len(subtree[s])==1:
                res.append(node)
            subtree[s].append(node)
            return s
        findSubtree(root)
        print(res)
        return res

        
