"""
LinkedIn offers the ability to create online job postings. Many members post jobs on LinkedIn network.
Some of the marketing team's goals are (1) to acquire new job posters that post jobs on LinkedIn's platform and
(2) to increase the number of jobs posted overall.
At the end of the day, the marketing team would like to measure how many job postings they have successfully acquired.

Sample job posting dataset is like below (JOB_ID is a unique key)

JOB_ID, MEMBER_ID, job_posting_date
1001,   1,         2017-04-14
1002,   1,         2017-08-14
1003,   2,         2017-05-31
1004,   3,         2016-08-23
1005,   3,         2017-04-28
1006,   3,         2017-05-23
1007,   3,         2017-07-08
Here introduce a marketing acquisition concept,

New job posting: Job posting by a member who's never posted a job on LinkedIn platform before
Repeat job posting: Job posting by member who has posted a job on LinkedIn platform before
"""

"""
sql: Let's introduce a new concept Reactivation job posting, 
which refers to job posting by a member who's posted a job before but not in the previous 180 days. 
For example, Job_ID 1005 is a Reactivation job posting. With the new concept, the question is,
 how many New job posting/Repeat job posting/Reactivation job postings are in the given table/file?
with post as{
select 
    rank()over(partition by member_id order by job_posting_date asc) as rnk,
    lead(job_posting_Date)over(partition by member_id order by date asc) as next_date
from 
    post    
}
select sum(case when rnk = 1  then 1 else 0 end) as newpost,
        sum(case when rnk = 2  then 1 else 0 end) as repetative,
        sum(case when date_diff(next_date, job_posting_date) > 180 then 1 else 0) as reactive_post
from
    post
"""
import pandas as pd

jobs = pd.DataFrame({"JOB_ID": [1001, 1002, 1003, 1004, 1005, 1006, 1007],
                     "MEMBER_ID": [1, 1, 2, 3, 3, 3, 3],
                     "job_posting_date": ["2017-04-14", "2017-08-14", "2017-05-31", "2016-08-23", "2017-04-28",
                                          "2017-05-23", "2017-07-08"]})
jobs["job_posting_date"] = jobs.apply(lambda x: pd.to_datetime(x["job_posting_date"]), axis=1)
jobs["rnk"] = jobs.groupby("MEMBER_ID")["job_posting_date"].rank(method="dense", ascending=True)
jobs["post_lead"] = jobs.groupby("MEMBER_ID")["job_posting_date"].shift(-1)
jobs["diff"] = (jobs["post_lead"] - jobs["job_posting_date"]).dt.days
jobs["react"] = jobs.apply(lambda x: 1 if x["diff"] > 180 else 0, axis=1)
jobs["new"] = jobs.apply(lambda x: 1 if x["rnk"] == 1 else 0 , axis=1)
totaljob = jobs["JOB_ID"].count()
react = jobs["react"].sum()
new = jobs["new"].sum()
print(jobs)
summary = pd.DataFrame({"newjob": [new], "reactive": [react], "repeat" : [totaljob - (react + new)]})
print(summary)