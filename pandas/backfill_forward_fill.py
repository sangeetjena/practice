"""
Problem Statement
A campaign snapshot table is as below which shows the start date, end date, and the latest budget for each campaign.
campaign_id | start_date |  end_date  | budget
-------------+------------+------------+--------
        1001 | 2020-08-01 | 2020-08-05 |     50
        1002 | 2020-08-06 | 2020-08-08 |     20
A campaign budget change history table is as below. As indicated in the data, one advertiser could change the budget multiple times on a particular day.

campaign_id |      change_dt      | old_value | new_value
-------------+---------------------+-----------+-----------
        1001 | 2020-08-03 10:00:00 |        10 |        20
        1001 | 2020-08-03 11:00:00 |        20 |        30
        1001 | 2020-08-04 15:00:00 |        30 |        50
Warm-up questions
How can we expand the snapshot table to all the dates that the campaign has been running from the start date to the end date? Below is the expected output.
campaign_id | event_date | budget
-------------+------------+--------
        1001 | 2020-08-01 |     50
        1001 | 2020-08-02 |     50
        1001 | 2020-08-03 |     50
        1001 | 2020-08-04 |     50
        1001 | 2020-08-05 |     50
        1002 | 2020-08-06 |     20
        1002 | 2020-08-07 |     20
        1002 | 2020-08-08 |     20
The change history table has multiple records for a day. Can you build a daily summary change table as below? The daily summary table should take the oldest old_value and the newest new_value for that day.
campaign_id | change_date | old_value | new_value
-------------+------------+-----------+-----------
        1001 | 2020-08-03 |        10 |        30
        1001 | 2020-08-04 |        30 |        50
Main question
With the above information, can you build a DAILY time series showing the budget for each campaign during the
whole cycle of the campaign? The data will show the budget by the end of each day for each campaign,
which means it should take the new_value of the day if there is a record in the change history table.
In addition, for days that are not in the change history table, it should be forward filled by the new_value
and backfilled by the old_value. The expected result is as below.

campaign_id | event_date | budget
-------------+------------+--------
        1001 | 2020-08-01 |     10
        1001 | 2020-08-02 |     10
        1001 | 2020-08-03 |     30
        1001 | 2020-08-04 |     50
        1001 | 2020-08-05 |     50
        1002 | 2020-08-06 |     20
        1002 | 2020-08-07 |     20
        1002 | 2020-08-08 |     20
Hints (In the below order)
For the first warm-up question, if the candidate is not familiar with unnest or lateral view explode. One can use a dummy table with all the possible dates to simplify the question into a simple join.
For SQL solutions to the main question, one of the difficulties is to backfill and forward fill the missing values. When joining two tables from answers for two warm-up questions, the correct way is to fill old_value backwards and new_value forwards. The interviewer can use the below table to hint at the candidate. If the candidate cannot come up with a solution in SQL/Scala, the interviewer can give a hint on the window functions - first_value() and last_value(). In Python, the interviewer can give a hint for bfill() and ffill() functions.


campaign_id | budget | event_date | old_value | new_value
-------------+--------+------------+-----------+-----------
        1001 |     50 | 2020-08-01 |      ->10 |
        1001 |     50 | 2020-08-02 |      ->10 |
        1001 |     50 | 2020-08-03 |        10 |        30
        1001 |     50 | 2020-08-04 |        30 |        50
        1001 |     50 | 2020-08-05 |           |      ->50
        1002 |     20 | 2020-08-06 |           |
        1002 |     20 | 2020-08-07 |           |
        1002 |     20 | 2020-08-08 |           |
Follow-up question
Can you re-write the answer to the main question in another language, such as Python, R, or Scala?
"""

import pandas as pd

dummy_date = pd.DataFrame({
    "date": ["2020-08-01", "2020-08-02", "2020-08-03", "2020-08-04", "2020-08-05", "2020-08-06", "2020-08-07",
             "2020-08-08"]
})

print(dummy_date)
campaign = pd.DataFrame({
    "campaign_id": ["1001", "1002"],
    "start_date": ["2020-08-01", "2020-08-06"],
    "end_date": ["2020-08-05", "2020-08-08"],
    "budget": ["50", "40"]
})

# cross join approach 1
# campaign["id1"] = 1
# dummy_date["id1"] = 1
# result = pd.merge(campaign, dummy_date, on="id1")

# cross join approach 2
result = campaign.merge(dummy_date, how="cross")
result = result[(result["date"] >= result["start_date"]) & (result["date"] <= result["end_date"])]
print(result)
result = result[["campaign_id", "start_date", "end_date", "budget", "date"]]
print(result)

# find olderst value and new value from the budget change history rable

budget_change = pd.DataFrame({"campaign_id": ["001", "001", "001"],
                              "change_dt": ["2020-08-03 10:00:00", "2020-08-03 11:00:00", "2020-08-04 15:00:00"],
                              "old_value": [10, 20, 30], "new_value": [20, 30, 50]})

budget_change["change_dt1"] = budget_change["change_dt"].apply(lambda x: pd.to_datetime(x).date())
budget_change["rnk1"] = budget_change.groupby(["campaign_id", "change_dt1"])["change_dt"].rank(method="dense",ascending=True)
budget_change["rnk2"] = budget_change.groupby(["campaign_id", "change_dt1"])["change_dt"].rank(ascending=False)
budget_change["val"] = budget_change.apply(lambda x: x["old_value"] if x["rnk1"] == 1.0 else 0, axis=1)
budget_change["val2"] = budget_change.apply(lambda x: x["new_value"] if x["rnk2"] == 1.0 else 0, axis=1)
result = budget_change.groupby(["campaign_id", "change_dt1"]).aggregate({"val":["sum"], "val2":["sum"]})
print(budget_change)
print(result)