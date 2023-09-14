def max_rods_price(cuts, price, n):
    temp_sum = [0 for i in range(n+1)]
    for ln in range(1,n+1):
        for cut in range(0, len(cuts)):
            if(cuts[cut] <= ln ):
                print(ln,cut)
                temp_sum[ln] = max(temp_sum[ln], price[cut] + temp_sum[ln-cuts[cut]])
    print(temp_sum)
    return temp_sum[n]


print(max_rods_price([1,2,5], [1,3,4], 5))