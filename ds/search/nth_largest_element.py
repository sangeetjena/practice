def n_largestelement(n, arr):
    prorityqueue = []
    for i in arr:
        print(i)
        print(prorityqueue)
        if prorityqueue.__len__()==0:
            prorityqueue.append(i)
        elif i<prorityqueue[0]:
            continue
        elif i>prorityqueue[-1]:
            if(prorityqueue.__len__()>=n):
                print("enter")
                del prorityqueue[0]
            prorityqueue.append(i)
        else:
            del prorityqueue[0]
            for j in range(0,len(prorityqueue)):
                if prorityqueue[j]>i:
                    prorityqueue=prorityqueue[0:j]+[i]+prorityqueue[j:]
                    break
    print(prorityqueue)

arr=[1,2,5,9,4,3,8]
n_largestelement(3,arr)