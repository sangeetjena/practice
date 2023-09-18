def valid_palindrom(str):
    p1 = 0
    p2 = len(str)-1
    while(p1 < p2):
        if str[p1] != str[p2]:
            return False
        p1+=1
        p2-=1
    return True

print(valid_palindrom("helleh"))