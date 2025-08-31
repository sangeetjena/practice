"""
https://leetcode.com/problems/non-negative-integers-without-consecutive-ones/description/

Given a positive integer n, return the number of the integers in the range [0, n] whose binary representations do not contain consecutive ones.

 

Example 1:

Input: n = 5
Output: 5
Explanation:
Here are the non-negative integers <= 5 with their corresponding binary representations:
0 : 0
1 : 1
2 : 10
3 : 11
4 : 100
5 : 101
Among them, only integer 3 disobeys the rule (two consecutive ones) and the other 5 satisfy the rule. 
Example 2:

Input: n = 1
Output: 2
Example 3:

Input: n = 2
Output: 3


Note: this is very similar to the number of ones digit dp problem, only difference is insteed of taking number, convert number to binary 
number and take the length as i and number can vary between 0 or 1.
"""
class Solution:
    def findIntegers(self, n: int) -> int:
        # similar to number of 1s in the digiti dp pattern
        # only difference is here insteed of taking all digits we are free to take only 0 or 1.
        # if previous index postion gave 0 then we are free to take o or 1 else ony 0 we can take.
        num = ""
        dp = {}
        def convertNumToBinary(n:int)-> str:
            if n ==0 :
                return "0"
            bits = []
            while n >0:
                bits.append(str(n%2))
                n//=2
            return "".join(reversed(bits))

        #@lru_cache(None)  --- this will do the same thing that we are doing using mmoization.
        def maxNums(i, prev_digit, tight, count):
            if (i, prev_digit, tight) in dp:
                return dp[(i, prev_digit, tight)]
            if i>= len(num):
                # why return 1 not count? because if we have reach to the end than one valid binary number we have found , because all the binary number that has consicutive number already would have eliminated
                # in comparition to the no of ones, where when we get one 1, we record the count, not waiting to reach to the end digit but in this problem when we reach to the end digit we are finding one valid binary number so we are recording it.
                return 1
            rng = int(num[i]) if tight else 1
            ans = temp = 0
            for d in range(rng+1):
                
                newtight  = tight and str(d) == num[i]
                if str(d) == '0' or prev_digit != '1':
                    temp = 1
                else: 
                    continue
                # print("index {}, digit {}, previous value {}".format(i,d, prev_digit))
                ans+= maxNums(i+1, str(d), newtight, count+temp)
                temp=0
            dp[(i, prev_digit, tight)] = ans
            return ans
        num = convertNumToBinary(n)
        print(num)
        return maxNums(0,'0',True, 0)
