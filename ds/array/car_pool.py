"""
Problem Statement
Given a car with a certain capacity for empty seats, the vehicle can only drive in one direction,
and initially, the car is at starting point. There is an array of trips, where each trip is represented by a list of 3 integers:
total_passengers: number of passengers for the trip.

start_from: the starting point of the trip, represented as the number of kilometres due from the car's starting point.

end_to: the ending point of the trip, represented as the number of kilometres due from the car's starting point.

The task is to determine if it is possible to pick up and drop off all passengers for all the given trips.
The solution should return true if it is possible and false otherwise.

Example
trips = [[1, 1, 3], [2, 2, 6], [3, 5, 9]]

[passenger, in, out]

capacity = 5

Output = true

Explanation
So, on the first trip [1,1,3], one passenger travels from 1 to 3. From 2 two more passengers are added by the trip second [2,2,6], and the total passenger becomes 3. At 3 first trip ends, and the total number of passengers becomes 2. The number of passengers remained the same till 5 where 3 passengers added at 5 by trip third, so total passengers become 5. At 6 the second trip ends, and the total number of passengers becomes 3 and remains the same till 9.

Which follows the capacity of the car, which is 5.
"""
def car_pool(arr, capacity):
    car_in = {x[1]: x[0] for x in arr}
    car_out = {x[2]: x[0] for x in arr}
    lst_in = sorted([x[1] for x in arr], reverse=False)
    lst_out = sorted([x[2] for x in arr], reverse=False)
    s = 0
    e = 0
    cnt = 0
    while e < len(car_in) and s < len(car_in):
        if lst_out[e]>lst_in[s]:
            cnt = cnt + car_in[lst_in[s]]
            s+=1
        else:
            cnt = cnt - car_out[lst_out[e]]
            e +=1
        if cnt > capacity:
            return False
    return True


trips = [[1, 1, 3], [2, 2, 6], [3, 5, 9]]
capacity = 5
print(car_pool(trips,capacity))

trips = [[5, 0, 4], [2, 4, 6], [3, 5, 7], [5,6,8]]
capacity = 7
print(car_pool(trips,capacity))