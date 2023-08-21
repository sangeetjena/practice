import pandas as pd

"""
Question : Identify users who logged in on 3 successive days in 2021
user_id    login_date        
1001       2021-12-28  
1001       2021-12-30   
1001       2021-12-31  
1002       2021-02-04  
1003       2021-02-05  
1003       2021-02-06  
1003       2021-02-07
"""
def sub_str(x):
    return x.split("-")[-1]

df = pd.DataFrame({"user_id": [1001, 1001, 1001, 1002, 1003, 1003, 1003],
                   "login_date": ["2021-12-28", "2021-12-30", "2021-12-31", "2021-02-04", "2021-02-05", "2021-02-06",
                                  "2021-02-07"]})
df["rnk"] = df.groupby(df['user_id']).rank(ascending=True)
df["day"] = df["login_date"].str[8:]
# df["day"] = df["login_date"].apply(sub_str)
# df["day"] = df["login_date"].transform(sub_str)
df["grp"] = df["day"].map(int) - df["rnk"]
# aggregate will reduce the value but will create new dat
# a frame. we can't store in same data frame.
print(df.groupby(["grp", "user_id"]).aggregate({"user_id": ["count"]}))
print(df.groupby(["grp", "user_id"]).filter(lambda x: x["user_id"].count() > 2))
# transform will allow to store group value into new column
df["count"] = df.groupby(["grp", "user_id"])["user_id"].transform("count")
print(df)
print(df[(df["user_id"] == 1003) & (df["count"] > 2)])
print(df.query("count > 2 and user_id == 1003"))
