```
https://leetcode.com/problems/binary-tree-level-order-traversal/

Given the root of a binary tree, return the level order traversal of its nodes' values. (i.e., from left to right,
level by level).

```
<img width="368" height="591" alt="image" src="https://github.com/user-attachments/assets/6b825621-fa33-4186-8729-61ccfd6c4576" />


```python
from collections import deque
class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if not root:
            return None
            
        levels = [] # List of Lists
        queue = deque( [root] ) # At 1st, Placing Root Node into the Queue

        while queue: # Traversing through Queue
            # Getting Current Level Size
            cur_level_size = len(queue)
            cur_level = [] # List to Stores Val's of Current Level
            
            for _ in range(cur_level_size):
                # Take the Front Guy
                front = queue.popleft()
                 
                # Store Front Node in Current Level List
                cur_level.append(front.val)

                # Appending the Left & Right Child of Front Node, If Exist
                if front.left:
                    queue.append(front.left)
                if front.right:
                    queue.append(front.right)
            
            # After While Loop, cur_level(List) contains Values of One Level
            # So, Appending the List in Answer List
            levels.append(cur_level)

        return levels
```
