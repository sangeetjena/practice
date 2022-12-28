import functools
def equalSum(lst,k):
    equalSumLst=[]
    if (lst.__len__()%k!=0):
        print("this no can't be devided to equal parts")
    else:
        lst=sorted(lst,reverse=True)
        print(lst)
        totalSum=functools.reduce(lambda a,b:a+b,lst)
        trgetValue=totalSum/k
        totalSum += lst[0]
        for i in range(0,k):
            equalSumLst.append([lst[0]])
            del lst[0]
        for i in reversed(range(0,lst.__len__())):
            enter=0
            for y in range(0,equalSumLst.__len__()):
                if(functools.reduce(lambda a,b :a+b,equalSumLst[y])+lst[i]<= trgetValue):
                    equalSumLst[y].append(lst[i])
                    enter=1
                    break
            if enter==0:
                break
        return  equalSumLst
print(equalSum([1,2,1,4,3,1],3))


