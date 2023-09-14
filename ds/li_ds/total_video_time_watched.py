def total_video_time(arr):
    video_arr = sorted(arr)
    total_times = []
    print(video_arr)
    for vid in video_arr:
        if len(total_times) ==0:
            total_times.append(vid)
            continue
        print(vid, total_times[-1][0])
        if total_times[-1][0]<=vid[0] and total_times[-1][1]>= vid[0]:
            print("in")
            x = total_times[-1][0]
            y = max(vid[1], total_times[-1][1] )
            del total_times[-1]
            total_times.append((x,y))
        else:
            total_times.append(vid)

    return total_times

print(total_video_time([(5, 7), (11, 116), (3, 4), (10, 12), (6, 12)]))