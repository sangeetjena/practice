# find next closest time using only the digits available in a time

def find_next_closest_time(time):
    hour, min = time.split(":")

    def validatime(hour, min):
        if hour > 23 or min > 59:
            return False
        return True
    def diffin_time(hr, mint):
        if int(hr)< int(hour) or (int(hr) == int(hour) and int(mint)< int(min)):
            diffhr = (11 - int(hour)) + int(hr)
            diffmin = (60 - int(min)) + int(mint)
            return (diffhr, diffmin)
        else:
            return ()


    h1 = hour[0]
    h2 = hour[1]
    m1 = min[0]
    m2 = min[1]
    lst = [h1, h2, m1, m2]
    for hr1 in lst:
        for hr2 in lst:
            for mn1 in lst:
                for mn2 in lst:
                    new_time = h1 + h2 + ":" + mn1 + mn2

