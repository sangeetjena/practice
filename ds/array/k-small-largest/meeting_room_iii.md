```
You are given an integer n. There are n rooms numbered from 0 to n - 1.

You are given a 2D integer array meetings where meetings[i] = [starti, endi] means that a meeting will be held during the half-closed time interval [starti, endi). All the values of starti are unique.

Meetings are allocated to rooms in the following manner:

Each meeting will take place in the unused room with the lowest number.
If there are no available rooms, the meeting will be delayed until a room becomes free. The delayed meeting should have the same duration as the original meeting.
When a room becomes unused, meetings that have an earlier original start time should be given the room.
Return the number of the room that held the most meetings. If there are multiple rooms, return the room with the lowest number.

A half-closed interval [a, b) is the interval between a and b including a and not including b.

 

Example 1:

Input: n = 2, meetings = [[0,10],[1,5],[2,7],[3,4]]
Output: 0
Explanation:
- At time 0, both rooms are not being used. The first meeting starts in room 0.
- At time 1, only room 1 is not being used. The second meeting starts in room 1.
- At time 2, both rooms are being used. The third meeting is delayed.
- At time 3, both rooms are being used. The fourth meeting is delayed.
- At time 5, the meeting in room 1 finishes. The third meeting starts in room 1 for the time period [5,10).
- At time 10, the meetings in both rooms finish. The fourth meeting starts in room 0 for the time period [10,11).
Both rooms 0 and 1 held 2 meetings, so we return 0. 
Example 2:

Input: n = 3, meetings = [[1,20],[2,10],[3,5],[4,9],[6,8]]
Output: 1
Explanation:
- At time 1, all three rooms are not being used. The first meeting starts in room 0.
- At time 2, rooms 1 and 2 are not being used. The second meeting starts in room 1.
- At time 3, only room 2 is not being used. The third meeting starts in room 2.
- At time 4, all three rooms are being used. The fourth meeting is delayed.
- At time 5, the meeting in room 2 finishes. The fourth meeting starts in room 2 for the time period [5,10).
- At time 6, all three rooms are being used. The fifth meeting is delayed.
- At time 10, the meetings in rooms 1 and 2 finish. The fifth meeting starts in room 1 for the time period [10,12).
Room 0 held 1 meeting while rooms 1 and 2 each held 2 meetings, so we return 1.

```



``` python
import heapq
class Solution:
    def mostBooked(self, n: int, meetings: List[List[int]]) -> int:
        rooms = [i for i in range(n)]
        room_count = [0 for i in range(n)]
        queue = []
        meetings.sort()
        currtime = -1
        heapq.heapify(rooms)
        heapq.heapify(queue)
        while len(meetings)>0:
            currtime+=1
            s,e = meetings[0]
            # don't allocte room if rooms are not available or meeting time has not reached.
            # this is to handle the condition, need to allocate meeting number with less number. is we will wait for meeting time then by that time we will be able to get all the meeting room available from which we can collect the least meeting number, else which ever meeting room released 1st will get allocated, which will not honor the above condition.
            if rooms and s <= currtime:
                room = heapq.heappop(rooms)
            else:
                room = None
            # if some available rooms are there then pull that room and book it till the end time.
            if room is not None:
                print("meeting room")
                meeting_end_time = e
                if currtime>s:
                    meeting_end_time = e + (currtime-s)
                heapq.heappush(queue, (meeting_end_time, room))
                room_count[room]+=1
                del meetings[0]
            # check if any meeting room has reach to its end time. then add it back to the available room.
            if queue and queue[0][0] <= currtime:
                heapq.heappush(rooms, heapq.heappop(queue)[1])
        max_meeting = 0


        # simpliy full the meeting room which has highest meeting and less in number.
        for i in range(len(room_count)):
            if room_count[max_meeting] < room_count[i]:
                max_meeting = i
        return max_meeting 


            
        

```
