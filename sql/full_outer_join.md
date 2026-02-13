
```
https://datalemur.com/questions/signup-confirmation-rate

```
<img width="805" height="1115" alt="image" src="https://github.com/user-attachments/assets/d4955118-1c3e-48f7-aa8d-aaf23f302a7d" />


``` sql

with total_user as (
select 
  count(distinct (
  case when emails.email_id is null 
  then texts.email_id 
  else emails.email_id end)) as total_user,
  count(distinct (
    case when texts.signup_action is not null and 
    texts.signup_action = 'Confirmed' then texts.email_id
    else null
    end
  )) as confirmed_users
from emails
full outer JOIN
texts
on (emails.email_id = texts.email_id)
)
select round((cast(confirmed_users as numeric)/total_user), 2) 
from total_user

```
