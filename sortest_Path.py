from copy import deepcopy
paths=[]
def find_shortest_path(metrix,start,end,visited,queue):
    moves=[[2,1],[2,-1],[-2,1],[-2,-1],[1,2],[1,-2],[-1,2],[-1,-2]]
    for jump in moves:
        x=jump[0]+start[0]
        y=jump[1]+start[1]
        if(x==end[0] and y==end[1]):
            paths.append(deepcopy(queue))
            print("reach to end")
            return
        if([x,y] in visited):
            continue
        if(x >0 and x<6 and y>0 and y < 6):
            visited.append([x,y])
            queue.append([x,y])
            find_shortest_path(metrix,[x,y],end,visited,queue)
            queue.remove([x,y])



if __name__ == '__main__':
    metrix=[[0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0]]
    start=[0,0]
    end=[6,6]
    visited=[]
    queue=[]
    find_shortest_path(metrix,start,end,visited,queue)
    print(paths)
    print(visited)
