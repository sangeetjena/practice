"""
https://platform.stratascratch.com/coding/10367-aggregate-listening-data?code_type=7
"""
import pandas as pd
users = pd.DataFrame({"user_id":[1,2,3,1,3,1],
                      "song_id":["s1","s1","s1","s2","s2","s2"],
                      "duration":[1,2,4,5,8,2]})

print(users)
user_grp = users.groupby(["user_id"]).agg({"duration":["sum"],"song_id":["nunique"]}).reset_index()
user_grp.columns=["user_id","total listen time","unique songs"]
print(user_grp)