"""
source destination distance
pune, mumbai 800
mumbai, pune 800
bbsr blr 1500
"""
import pandas as pd
df = pd.DataFrame({"source": ["pune","mumbai","bbsr"],
              "destination": ["mumbai","pune","blr"],
              "distance": [800,800,1500]})
df["least"] = df[["source", "destination"]].min(axis=1)
df["greatest"] = df[["source","destination"]].max(axis=1)
# sumilar to row_num()over(partition by least, greatest order by least)
df["rnk"] = df.groupby(["least", "greatest"]).cumcount() +1
print(df[df["rnk"] == 1])