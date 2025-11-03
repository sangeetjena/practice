"""
https://www.geeksforgeeks.org/find-number-times-string-occurs-given-string/

Input: string = “subsequence”pattern = “sue” Output: 7 subsequencesubsequencesubsequencesubsequencesubsequencesubsequencesubsequence

Note: same as distinct subsequence, here insteed of taking max, take +
"""

# Function to count the number of times pattern `Y[0…n)`
# appears in a given string `X[0…m)` as a subsequence
def count(X, Y):
 
    (m, n) = (len(X), len(Y))
 
    # `T[i][j]` stores number of times pattern `Y[0…j)`
    # appears in a given string `X[0…i)` as a subsequence
    T = [[0 for x in range(n + 1)] for y in range(m + 1)]
 
    # if pattern `Y` is empty, we have found subsequence
    for i in range(m + 1):
        T[i][0] = 1
 
    '''
      If the current character of both string and pattern matches,
        1. Exclude current character from both string and pattern
        2. Exclude only the current character from the string
 
      Otherwise, if the current character of the string and pattern do not match,
      exclude the current character from the string
    '''
 
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            T[i][j] = (T[i - 1][j - 1] if (X[i - 1] == Y[j - 1]) else 0) + T[i - 1][j]
 
    # return last entry in the lookup table
    return T[m][n]
 
 
if __name__ == '__main__':
 
    X = 'subsequence'   # Input string
    Y = 'sue'           # Pattern
 
    print(count(X, Y))
