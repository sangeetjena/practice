# If the data volume on a particular day is greater than or equal to twice the median data volume in prior 'N' days, a notification will be sent. No notification will be sent until there are enough number of prior days data for calculating the median. Given number of days 'N' and daily data volume for a period of 'P' days, find and print the number of times the notification will be sent over all the 'P' days.
#
# For example, consider data volumes = [10, 20, 30, 40, 35] and N = 3 . On the first three days, no notification will be sent. On day 4, trailing data volumes are [10, 20, 30], the median is 20 and the day's data volume is 40. Since 40 >= 2 x 20 , notification will be sent.
#
# On day 5, trailing data volumes are [20, 30, 40]. Median is 30. Data volume of the day is 35, which is less than 2 x 30, no notification will be sent. Over the period of 5 days, only one notification was sent.
#
import statistics
def notice(arr, n):
    cnt = 0
    for i in range(n, len(arr)):
        x = statistics.median(arr[i-n:i-1]) * 2
        if arr[i] >= x:
            cnt+=1
    return cnt

print(notice([10, 20, 30, 40, 35], 3))