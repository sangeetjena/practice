import datetime
def date_diff(date1: str, date2: str):
    # d1 = datetime.datetime.strptime(date1, '%Y-%m-%d')
    # d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    # diff = abs((d1-d2).days)
    # return diff
    month_yr = {1:31,2:28,'3':31,'4':30,'5':31,6:30,'7':31,'8':31,'9':30,'10':31,'11':30,'12':31}
    y1,m1,d1 = [int(x) for x in date1.split('-')]
    y2,m2,d2 = [int(x) for x in date2.split('-')]
    days = 0
    if y1 == y2:
        for m in range(m2, m1):
            days = days + month_yr[m]
        days = days - d1
        days = days - (month_yr[m2]-d2)
    print(days)

date_diff('2019-06-29', '2019-06-30')