import math

#solution  : first break string into substring of k int and convert it in to a int; and store it in a list
# find max int possible by taking all k int as 1 .
# then find int from 0 to max num
# find if each number present in the list
def convertBitTOInt(string):
    sum=0
    for i in reversed(range(0,len(string))):
        if string[i]!='0':
            sum+=math.pow(2,i)
    return sum

def binaryCodeSearch(string:str,k):
    decode=[]
    for i in range(0,len(string)-k+1):
        decode.append(convertBitTOInt(string[i:i+k]))
    # find no of combination of number from 0 to all digit 1
    #ex : k=2 then 11 - > 2^0+2^1 = 3
    maxnum=1
    notexists = 0
    for i in range(1,k):
        maxnum+=int(math.pow(2,i))
    for i in range(0,maxnum):
        notexists = 0
        if i in decode:
            notexists = 1
        if notexists==0:
            break
    if notexists==0:
        print("false")
    else:
        print("true")

binaryCodeSearch("0110",2)


