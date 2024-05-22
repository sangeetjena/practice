"""
https://www.hackerrank.com/challenges/full-score/problem?isFullScreen=true
  
"""
with challenge as (
select
    sub.hacker_id,
    sub.challenge_id,
    sub.score,
    diff.score - sub.score as diff_score
    from 
    submissions sub
    join
    challenges ch 
    on (sub.challenge_id= ch.challenge_id)
    join difficulty diff
    on(diff.difficulty_level = ch.difficulty_level)
)
select 
hk.hacker_id,
hk.name
from challenge ch
join
hackers hk
on(hk.hacker_id = ch.hacker_id)
where diff_score = 0
group by hk.hacker_id, hk.name
having count(distinct(ch.challenge_id))>1;
