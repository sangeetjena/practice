"""
https://leetcode.com/problems/game-play-analysis-iv/description/?envType=study-plan-v2&envId=top-sql-50

  Table: Activity

+--------------+---------+
| Column Name  | Type    |
+--------------+---------+
| player_id    | int     |
| device_id    | int     |
| event_date   | date    |
| games_played | int     |
+--------------+---------+
(player_id, event_date) is the primary key (combination of columns with unique values) of this table.
This table shows the activity of players of some games.
Each row is a record of a player who logged in and played a number of games (possibly 0) before logging out on someday using some device.
 

Write a solution to report the fraction of players that logged in again on the day after the day they first logged in, rounded to 2 decimal places. In other words, you need to count the number of players that logged in for at least two consecutive days starting from their first login date, then divide that number by the total number of players.

The result format is in the following example.


"""
# Write your MySQL query statement below
with player_lead as (
    select 
        player_id,
        event_date,
        lead(event_date,1, event_date)over(partition by player_id order by event_date asc) as next_date,
        rank()over(partition by player_id order by event_date asc) as rnk
    from activity
)
select 
    round(sum( case when datediff(next_date, event_date) = 1 then 1 else 0 end)/count(distinct player_id),2) as fraction
from
    player_lead
where
    rnk = 1



    
