from typing import List


class Solution:
    def findCheapestPrice(
        self, n: int, flights: List[List[int]], src: int, dst: int, k: int
    ) -> int:
        weightedPaths = [9999 for x in range(len(flights))]
        steps = [0 for x in range(len(flights))]
        visited = []
        dfs = []
        if src not in [x[0] for x in flights]:
            return -1
        weightedPaths[src] = 0
        # initialisation of bfs
        dfs.append([src, src, 0])
        while len(dfs) != 0:
            point = dfs[-1]
            del dfs[-1]
            if point in visited:
                continue
            visited.append(point)
            src1, dst1, cost = point
            weightedPaths[dst1] = min(weightedPaths[dst1], weightedPaths[src1] + cost)
            steps[dst1] = steps[src1] + 1
            if dst1 == dst or steps[dst1] - 1 > k:
                continue
            for pnt in flights:
                if pnt in visited or dst1 != pnt[0]:
                    continue
                dfs.append(pnt)
        if weightedPaths[dst] == 9999:
            return -1
        print(weightedPaths)
        print(steps)
        return weightedPaths[dst]


obj = Solution()
flights = [[1,2,10],[2,0,7],[1,3,8],[4,0,10],[3,4,2],[4,2,10],[0,3,3],[3,1,6],[2,4,5]]
obj.findCheapestPrice(1, flights, 0, 4, 1 )