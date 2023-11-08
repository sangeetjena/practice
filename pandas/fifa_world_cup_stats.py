"""
learn : union/concat
2018-06-14	Group Stages	A	Russia	5	Saudi Arabia	0
2018-06-14	Group Stages	A	Egypt	0	Uruguay	1
2018-06-14	Group Stages	B	Portugal	3	Spain	3
2018-06-20	Group Stages	A	Russia	3	Egypt	1
2018-06-20	Group Stages	A	Uruguay	1	Saudi Arabia	0
2018-06-25	Group Stages	A	Saudi Arabia	2	Egypt	1
2018-06-25	Group Stages	A	Uruguay	3	Russia	0

"""
import pandas as pd
foodball = pd.DataFrame({"date": ["2018-06-14","2018-06-14","2018-06-14", "2018-06-20", "2018-06-20", "2018-06-25", "2018-06-25"],
                         "group" : ["A","A","B","A","A","A","A"],
                         "country1": ["Russia", "Egypt", "Portu", "Russia", "Urg", "Saudi", "Urg"],
                         "goal1" : [5,0,3,3,1,2,3],
                         "country2" : ["Saudi", "Urg", "Spain", "Egypt", "Saudi", "Egypt", "Russia"],
                         "goal2" : [0,1,3,1,0,1,0]})


df1 = foodball[["country1", "goal1"]].rename(columns={"country1": "country", "goal1":"goal"})
df2 = foodball[["country2", "goal2"]].rename(columns={"country2": "country", "goal2":"goal"})

df = pd.concat([df1, df2], ignore_index=True)
print(df)

df3 = df.groupby("country")["goal"].sum().reset_index()
df3.columns=["country","sum"]
df3["rnk"] = df3["sum"].rank(method="dense", ascending=False)
print(df3[df3["rnk"] == 1])