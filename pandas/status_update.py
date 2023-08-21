import pandas as pd

"""
Problem Statement
 LinkedIn members can turn on and off push notification on the settings page. Members can ONLY turn it off when the status is on and they can ONLY turn it on when the status is off.

With that, we'd like to introduce the following questions:

1. How can we infer the "current_status" based on the information provided in "old_status" and "actions" tables (turning_on or turning_off)?

2. [Follow Up] If the "date" column is missing in "actions" table, how can we get the same desired output?



See below for the two tables we will use for this problem:

/*
TABLE 1:  "old_status" - contains all LinkedIn members' latest push notification setting status. Unfortunately, the data in this table is outdated.
*/

member_id    old_status
-------------------------------
     1         on
     2         off
     3         on
     4         off



/*
TABLE 2: "actions" - all actions that members made in May (after the time period of 'status' table).
(For simplicity, let's assume a member can have at most one action per day)
*/

member_id    date        action
-------------------------------
     1        5/2       turn_off
     1        5/5       turn_on
     2        5/3       turn_on
     4        5/10      turn_on
     4        5/13      turn_off



/* EXPECTED OUTPUT */

member_id   current_status
---------------------------------
     1            on
     2            on
     3            on
     4            off
SQL:

with x as (
select
    old.member_id,
    case when act.action is not null then act.action else old.old_action as status,
    rank()over(partition by old.member_id order by act.date desc) as rnk
from old_status old
left join
    action act
on (old.member_id = act.member_id)
)
select memebr_id, status from x where rnk=1

"""
df_old_status = pd.DataFrame({"member_id": [1, 2, 3, 4], "old_status": ["on", "off", "on", "off"]})

df_actions = pd.DataFrame({"member_id": [1, 1, 2, 4, 4],
                           "date": ["5/2", "5/5", "5/3", "5/10", "5/13"],
                           "action": ["turn_off", "turn_on", "turn_on", "turn_on", "turn_off"]})

df_status = df_old_status.merge(df_actions, how="left", left_on="member_id", right_on="member_id")
df_status.sort_values(by=["member_id", "date"], ascending=False, inplace=True)
df_status["date"].fillna("1/1", inplace=True)
df_status["action"].fillna("None", inplace=True)
df_status["rnk"] = df_status.groupby(["member_id"])["date"].rank(ascending=False)
print(df_status)

def case(x, y):
    encode = {"off": "off",
              "turn_off": "off",
              "on": "on",
              "turn_on": "on"}
    if y == "None":
        return encode[x]
    else:
        return encode[y]

df_status["status"] = df_status.apply(lambda x: case(x["old_status"], x["action"]), axis=1)
# OR
# encode = {"off": "off",
#               "turn_off": "off",
#               "on": "on",
#               "turn_on": "on"}
# df_status["status"] = df_status.apply(lambda x: encode[x["old_status"]] if x["action"] == "None" else encode[x["action"]]  , axis=1)
print(df_status[df_status["rnk"] == 1])
