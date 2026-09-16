"""
https://leetcode.com/problems/fruit-into-baskets/description/?utm_source=chatgpt.com

You are visiting a farm that has a single row of fruit trees arranged from left to right. The trees are represented by an integer array fruits where fruits[i] is the type of fruit the ith tree produces.

You want to collect as much fruit as possible. However, the owner has some strict rules that you must follow:

You only have two baskets, and each basket can only hold a single type of fruit. There is no limit on the amount of fruit each basket can hold.
Starting from any tree of your choice, you must pick exactly one fruit from every tree (including the start tree) while moving to the right. The picked fruits must fit in one of your baskets.
Once you reach a tree with fruit that cannot fit in your baskets, you must stop.
Given the integer array fruits, return the maximum number of fruits you can pick.

 

Example 1:

Input: fruits = [1,2,1]
Output: 3
Explanation: We can pick from all 3 trees.
Example 2:

Input: fruits = [0,1,2,2]
Output: 3
Explanation: We can pick from trees [1,2,2].
If we had started at the first tree, we would only pick from trees [0,1].
Example 3:

Input: fruits = [1,2,3,2,2]
Output: 4
Explanation: We can pick from trees [2,3,2,2].
If we had started at the first tree, we would only pick from trees [1,2].


Note: this is like sliding window problem, if there is already elements are there in the queue, before taking new element remove element in a order they entered in the basket.


"""


class Solution:
    def totalFruit(self, fruits: List[int]) -> int:
        l,r = 0,0
        # maintain a dict to track how many elements are there and count of element
        collect = {}
        maxlen = 0
        while r< len(fruits):
            if fruits[r] in collect.keys():
                collect[fruits[r]]+=1
            else:
                if len(collect)>1:
                    # check when new element comes and the count of existing element is >1 then 
                    # remove the elements which is there in the dict before taking new elemnet.
                    while len(collect)>1:
                        collect[fruits[l]]-=1
                        if collect[fruits[l]] <=0:
                            del collect[fruits[l]]
                        l+=1
                collect[fruits[r]] =1
            r+=1
            maxlen = max(maxlen, r-l)
        return maxlen

                   

