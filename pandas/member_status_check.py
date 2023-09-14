# / *
# TABLE
# 1: "old_status" - contains
# all
# LinkedIn
# members
# ' latest push notification setting status. Unfortunately, the data in this table is outdated.
# * /
#
# member_id    old_status
# -------------------------------
#      1         on
#      2         off
#      3         on
#      4         off
#
# / *
# TABLE 2: "actions" - all actions that members made in May (after the time period of 'status' table).
# (For simplicity, let's assume a member can have at most one action per day)
#
# member_id    date        action
# -------------------------------
# 1        5 / 2       turn_off
# 1        5 / 5       turn_on
# 2        5 / 3       turn_on
# 4        5 / 10      turn_on
# 4        5 / 13      turn_off
#
# / * EXPECTED OUTPUT * /
#
# member_id   current_status
# ---------------------------------
# 1            on
# 2            on
# 3            on
# 4            off

import pandas as pd

old_status = pd.DataFrame({"member_id": [1, 2, 3, 4],
                           "old_status": ["on", "off", "on", "off"]})
new_status = pd.DataFrame(
    {"member_id": [1, 1, 2, 4, 4],
     "date": ["2023-05-02", "2023-05-05", "2023-05-03", "2023-05-10", "2023-05-13"],
     "action": ["turn_off", "turn_on", "turn_on", "turn_on", "turn_off"]})
print(old_status)
print(new_status)
result = old_status.merge(new_status, on="member_id", how="left")
result["rnk"] = result.groupby(["member_id"])["date"].rank(method="dense", ascending="True")
print(result.columns)
cnt = result.groupby(["member_id"]).aggregate({"date": ["count", "sum"]})
# group by will create multi index data frame whose primary index will be memberid and primary column will be date
# and within date field count and sum will come
print(cnt)
print(cnt.index)
final = result[result["rnk"] == 1].merge(cnt["date"], on="member_id", how="inner")
final["curr_status"] = final[["old_status", "count"]].apply(
    lambda x: x["old_status"] if x["count"] % 2 == 0 else "off" if x["old_status"] == "on" else "on", axis=1)
print(final)
