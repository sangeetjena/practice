```
https://leetcode.com/problems/reconstruct-itinerary/description/
You are given a list of airline tickets where tickets[i] = [fromi, toi] represent the departure and the arrival airports of one flight. Reconstruct the itinerary in order and return it.

All of the tickets belong to a man who departs from "JFK", thus, the itinerary must begin with "JFK". If there are multiple valid itineraries, you should return the itinerary that has the smallest lexical order when read as a single string.

For example, the itinerary ["JFK", "LGA"] has a smaller lexical order than ["JFK", "LGB"].
You may assume all tickets form at least one valid itinerary. You must use all the tickets once and only once.



Note:


```
<img width="687" height="724" alt="image" src="https://github.com/user-attachments/assets/7c7d50f1-a603-4b36-8e17-f5f375d311c9" />


``` python
class Solution:
    def findItinerary(self, tickets: List[List[str]]) -> List[str]:
        # Create a graph represented as a dictionary where each airport is a key, and its destinations are values.
        graph = defaultdict(list)

        for departure, arrival in sorted(tickets, reverse=True):
            graph[departure].append(arrival)

        # Initialize the stack with the starting airport "JFK" and an empty itinerary.
        st = ["JFK"]
        new_itinerary = []

        while st:
            # If there are destinations from the current airport, add the next destination to the stack.
            if graph[st[-1]]:
                st.append(graph[st[-1]].pop())
            else:
                # When there are no more destinations, add the current airport to the new itinerary.
                new_itinerary.append(st.pop())

        # Reverse the new itinerary to get the correct order.
        return new_itinerary[::-1]
```
