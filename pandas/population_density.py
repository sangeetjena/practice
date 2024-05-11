"""
You are working on a data analysis project at Deloitte where you need to analyze a dataset containing information
about various cities. Your task is to calculate the population density of these cities, rounded to the nearest integer, and identify the cities with the minimum and maximum densities.
The population density should be calculated as (Population / Area).


The output should contain 'city', 'country', 'density'.

https://platform.stratascratch.com/coding/10368-population-density?code_type=7
"""
import pandas as pd
import math
df = pd.DataFrame({"city": ["bbsr","bangalore","miniapolis"],
                   "country":["ind", "ind", "usa"],
                   "population": [10, 20, 5],
                   "area": [3,4,5]})
df["density"] = df["population"]/ df["area"]
print(df)
df["density"] = df["density"].apply(lambda x:math.ceil(x))
df["rnk1"] = df["density"].rank(ascending=True).astype(int)
df["rnk2"] = df["density"].rank(ascending=False).astype(int)
print(df.query("rnk1 == 1.0 or rnk2 == 1.0"))