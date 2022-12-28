"""
Q. find longest substring without repeating charector
approach :
    i need a list to store the charector i am parsing, this will help to identify duplicate char
    store the longest string in a variable and replace if found new long str.

    i will need single loop and where i will find duplicate will break the continuity and store
    longest str and continuie with next chr to search for new long str.
"""

"""
code work through:
    i have taken two variable to hold longest string and on tmpword to hold current string
    then i check if the current string is longer than longword then i replace longword with temword and store last char in temword
    i will continue this until i reach to the last char, then again i will check if the longest word is empty and then i will finally replace longword with tempword else leave
"""
def longestSubstr(word):
    longWord=""
    tmpWord=""
    for i in range(0,word.__len__()):
        if word[i] in tmpWord:
            if len(longWord) < len(tmpWord):
                longWord=tmpWord
                tmpWord=word[i]
            else:
                tmpWord = word[i]
        else:
            tmpWord+=word[i]
        if i==len(word) and longWord.__len__()==0:
            longWord=tmpWord
    return longWord

print(longestSubstr("sangeetkumarjena"))

