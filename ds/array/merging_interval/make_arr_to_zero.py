"""
https://leetcode.com/problems/zero-array-transformation-i/description/?envType=company&envId=google&favoriteSlug=google-thirty-days

Solution:  https://www.youtube.com/watch?v=hOEg26zHlco
Note: create difference set, 
      after increament value for a sub set all the difference in value of the subset will remain same, 
      so we can say for a subset what really change is starting element of the subset and end +1 element in the subset.
      2- after all the operation if cumilative difference eqal to the element , then the ele,ent can become 0.
"""
