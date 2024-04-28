"""
design a report to tell what is the 90, 180, 270, 365 piled up inventory there in the
warehouse as of today.
https://www.youtube.com/watch?v=xN2PRAd8IZQ&list=PLavw5C92dz9Fahr7taauUx5RnTfuGyL--&ab_channel=techTFQ
"""
import pandas as pd
import datetime
warehouse_df = pd.DataFrame({"ID":["TR001","TR002","TR003","TR004","TR005","TR006","TR007","TR008","TR009","TR0010","TR0011","TR0012","TR0013"],
                             "OnholdQuantity": [250,242,362,335,334,205,203,246,346,346,346,377,278],
                             "OnholdQuantityDelta": [250,8,120,27,1,129,2,43,102,1,1,31,99],
                             "event_type": ["in","out","in","out","out","out","out","in","in","out","out","in","out"],
                             "event_date_time": ["20-05-2019 00:00", "22-05-2019 00:00", "31-12-2019 00:00","29-01-2020 00:00", "18-02-2020 00:00", "18-02-2020 00:10", "25-02-2020 00:00", "25-04-2020 00:00","25-04-2020 01:00", "23-05-2020 00:00", "24-05-2020 00:00","24-05-2020 01:00","25-05-2020 00:00"]})

print(warehouse_df)
# total dispatch inventory
total_out = warehouse_df.query("event_type == 'out'")["OnholdQuantityDelta"].sum()
# find cumilative sum of all incoming inventory
warehouse_df["cum_sum"] = warehouse_df.query("event_type == 'in'")["OnholdQuantityDelta"].cumsum()
print(warehouse_df[warehouse_df["event_type"] == "in"])
warehouse_df["balance"] = warehouse_df["cum_sum"] - total_out
warehouse_df["date_diff"] = (pd.to_datetime("26-05-2020 01:00") - warehouse_df["event_date_time"].apply(pd.to_datetime)).dt.days
def grouping(date_diff):
    if date_diff in range(0,91):
        return '0-91'
    if date_diff in range(91,181):
        return '91-180'
    if date_diff in range(181,271):
        return '181-270'
    else:
        return '270-365'
warehouse_df['rnk'] = warehouse_df[warehouse_df["event_type"] == "in"]["date_diff"].apply(grouping)
print(warehouse_df[warehouse_df["event_type"] == "in"][["ID", "cum_sum","event_date_time", "date_diff","balance", "rnk"]])

print(warehouse_df[warehouse_df["event_type"] == 'in']["OnholdQuantityDelta"].sum())
print(total_out)