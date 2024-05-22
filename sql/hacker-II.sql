"""
https://www.hackerrank.com/challenges/contest-leaderboard/problem?isFullScreen=true
"""

/*
Enter your query here.
Please append a semicolon ";" at the end of the query and enter your query in a single line to avoid error.
*/
with submission as (
select 
    hacker_id,
    challenge_id,
    max(score) as score
from 
    submissions sbm
group by hacker_id, challenge_id
)
select
hk.hacker_id,
hk.name,
sum(sbm.score) as max_score
from submission sbm
join hackers hk
on (hk.hacker_id = sbm.hacker_id)
group by hk.hacker_id, hk.name
having sum(sbm.score)>0
order by max_score desc , hk.hacker_id asc;
