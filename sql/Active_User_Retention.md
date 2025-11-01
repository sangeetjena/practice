```
This is the same question as problem #23 in the SQL Chapter of Ace the Data Science Interview!

Assume you're given a table containing information on Facebook user actions.
Write a query to obtain number of monthly active users (MAUs) in July 2022,
including the month in numerical format "1, 2, 3".

Hint:
An active user is defined as a user who has performed actions such as 'sign-in', 'like', or 'comment'
 in both the current month and the previous month.


```
<img width="481" height="613" alt="image" src="https://github.com/user-attachments/assets/8fb469f6-0694-471b-9bcb-069de2eafff1" />


``` sql
WITH prev_mn AS (
    SELECT a.user_id
    FROM user_actions a
    JOIN user_actions b
        ON a.user_id = b.user_id
    WHERE EXTRACT(MONTH FROM b.event_date) = 6
      AND EXTRACT(YEAR FROM b.event_date) = 2022
      AND EXTRACT(MONTH FROM a.event_date) = 7
      AND EXTRACT(YEAR FROM a.event_date) = 2022
)

SELECT 
    EXTRACT(MONTH FROM event_date) AS month,
    COUNT(DISTINCT user_id) AS user_count
FROM user_actions
WHERE user_id IN (SELECT user_id FROM prev_mn)
GROUP BY 
    EXTRACT(MONTH FROM event_date),
    EXTRACT(YEAR FROM event_date)
HAVING 
    EXTRACT(MONTH FROM event_date) = 7
    AND EXTRACT(YEAR FROM event_date) = 2022;


```
