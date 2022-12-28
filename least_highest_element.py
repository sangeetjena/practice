
elem = [1,2,3,2,4,5,1,6,6,3,3,3]
occurance={}
""" get count of occurrence """
for i in elem:
    if occurance.get(i):
        occurance[i] = occurance[i] + 1
    else:
        occurance[i] = 1
print(occurance)

prev_occ=9999999
prev_value=0
""" get least occurrence and largest element from the list occurrence elements"""
for i in occurance:
    if(prev_occ>=occurance[i]):
        if(prev_value<i):
            prev_value=i
            prev_occ=occurance[i]
print(prev_value)
