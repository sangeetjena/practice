"""
Problem Statement
-- INPUT DATA
-- table t1
-- date  qty_prod_a  qty_prod_b  qty_prod_c
-- 1/1/2013	100	   200	        300
-- 1/2/2013	101	     0		301
-- 1/3/2013	102	   202		302
--------------------------------------------------------------------------------------------------------
-- QUESTION
--	# you have a table t1 with the quantity of product A, B, and C sold per day, as shown above
--	# there are only 3 possible products in the table: A, B, and C
--	# write SQL code to reformat the data as shown below
--	# the resulting data should be in 3 columns: {date, product name, quantity sold}
--------------------------------------------------------------------------------------------------------
-- DESIRED OUTPUT
-- date  product_name   quantity_sold
-- 1/1/2013	A	100
-- 1/1/2013	B	200
-- 1/1/2013	C	300
-- 1/2/2013	A	101
-- 1/2/2013	C	301
-- 1/3/2013	A	102
-- 1/3/2013	B	202
-- 1/3/2013	C	302
"""
import pandas as pd

df = pd.DataFrame({"date": ["1/1/2013", "1/2/2013", "1/3/2013"],
                   "qty_prod_a": [100, 101, 102],
                   "qty_prod_b": [200, 0, 202],
                   "qty_prod_c": [300, 301, 302]})
print(df)
df_a = df[["date", "qty_prod_a"]].rename(columns={"qty_prod_a":"quantity"})
print(df_a )
df_a["prod"] = df_a.apply(lambda x:"A" if 1==1 else "", axis=1)
df_b = df[["date", "qty_prod_b"]].rename(columns={"qty_prod_b":"quantity"})
df_b["prod"] = df_b.apply(lambda x: "B" if 1==1 else "", axis=1)
df_c = df[["date", "qty_prod_c"]].rename(columns={"qty_prod_c":"quantity"})
df_c["prod"] = df_c.apply(lambda x: "C" if 1==1 else "", axis=1)

df_final = pd.concat([df_a,df_b,df_c], ignore_index=True)
print(df_final)