# Learn : fill na, sorting, groupby, lead, lag, filter
#
# When a member visits a page on LinkedIn (desktop or mobile app), a tracking event is logged by the client (browser or app). These events can be used to analyze page view statistics as well as how members navigate from one page to another.
#
# Problem Statement
# Due to a tracking bug, tracking event fired more than once when certain (not all) members visited the 'home' page on 2022-01-15. The data for this date is available as a dataframe 'pveDataFrame'. Sample data pasted below.
#
# Part 1: How do we identify and eliminate these erroneous events. For simplicity, we can assume that if a 'home' page event was fired within 1 second of previous 'home' page event by the member, it is an invalid record. In real word, time difference between subsequent events could be just few milliseconds.
# Part 2: After we have fixed the data, we need to determine: Which page receives most traffic right after member visits "home" on "2022-01-15"?
# Assume Data is available through pveDataFrame. A subset of the data for 2022-01-15 is shown. Dataframe could have other dates
# +-------------------+--------+-------+
# |           datetime|memberId| pageId|
# +-------------------+--------+-------+
# |2022-01-15 08:00:00|     100|   home|
# |2022-01-15 08:00:01|     100|   home| // within 1 second of previous home page view by same member ...consider as error
# |2022-01-15 08:00:05|     100|network|
# |2022-01-15 08:00:16|     100|   jobs|
# |2022-01-15 08:00:20|     100|   home|
# |2022-01-15 08:00:00|     200|   home|
# |2022-01-15 08:00:05|     200|   home| // within 5 seconds of previous home page view by same member ...consider as valid
# |2022-01-15 08:00:12|     200|network|
# |2022-01-15 08:00:20|     200|   jobs|
# |2022-01-15 08:00:25|     200|network|
# |2022-01-15 08:00:00|     300|   home|
# |2022-01-15 08:00:04|     300|network|
# |2022-01-15 08:00:10|     300|   home|
# |2022-01-15 08:00:10|     300|   home| // within 0 seconds of previous home page view by same member ...consider as error
# |2022-01-15 08:00:20|     300|   jobs|
# +-------------------+--------+-------+
import pandas as pd

pg_vw = pd.DataFrame({"datetime": ["2022-01-15 08:00:00",
                                   "2022-01-15 08:00:01",
                                   "2022-01-15 08:00:05",
                                   "2022-01-15 08:00:16",
                                   "2022-01-15 08:00:20",
                                   "2022-01-15 08:00:00",
                                   "2022-01-15 08:00:05",
                                   "2022-01-15 08:00:12",
                                   "2022-01-15 08:00:20",
                                   "2022-01-15 08:00:25",
                                   "2022-01-15 08:00:00",
                                   "2022-01-15 08:00:04",
                                   "2022-01-15 08:00:10",
                                   "2022-01-15 08:00:10",
                                   "2022-01-15 08:00:20"],
                      "memberId": [100,
                                   100,
                                   100,
                                   100,
                                   100,
                                   200,
                                   200,
                                   200,
                                   200,
                                   200,
                                   300,
                                   300,
                                   300,
                                   300,
                                   300],
                      "pageId": ["home",
                                 "home",
                                 "network",
                                 "jobs",
                                 "home",
                                 "home",
                                 "home",
                                 "network",
                                 "jobs",
                                 "network",
                                 "home",
                                 "work",
                                 "home",
                                 "home",
                                 "jobs" ]})
pg_vw["datetime"] = pg_vw.apply(lambda x:pd.to_datetime(x["datetime"]), axis=1 )
pg_vw["nextdatetime"] = pg_vw.sort_values(by=["memberId","datetime"], ascending=True).groupby("memberId")["datetime"].shift(1)
pg_vw.fillna(value="2000-01-01 00:00:00", inplace=True)
pg_vw["diff_date"] = (pg_vw["datetime"] - pg_vw["nextdatetime"]).dt.total_seconds()
print(pg_vw.sort_values(by=["memberId","pageId"]))
print("final miss fired events -")
print(pg_vw[pg_vw["diff_date"] < 2])
# print(pg_vw.query("diff_date < 2"))

x = pg_vw[pg_vw["pageId"] != "home"].groupby(["pageId"]).aggregate({"pageId":["count"]}).reset_index()
x.columns = ["pageId", "count"]
x["rnk"] = x["count"].rank(method="dense", ascending=False)
print(x[x["rnk"] == 1])