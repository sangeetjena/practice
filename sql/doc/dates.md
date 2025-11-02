Task                            |  MySQL Function                         |  SQL Server Function                    |  Without Function            
--------------------------------+-----------------------------------------+-----------------------------------------+------------------------------
Current Date                    |  CURDATE()                              |  CAST(GETDATE() AS DATE)                |  Not practical               
Current Date & Time             |  NOW()                                  |  GETDATE()                              |  Not practical               
Convert String to Date          |  STR_TO_DATE()                          |  CAST(), CONVERT()                      |  Manual parsing              
Extract Day, Month, Year        |  DAY(), MONTH(), YEAR()                 |  DATEPART(day/month/year, ...)          |  SUBSTRING date string       
Add/Subtract Dates              |  DATE_ADD(), DATE_SUB()                 |  DATEADD()                              |  Integer addition (rare)     
Last Day of Month               |  LAST_DAY()                             |  EOMONTH()                              |  Add 1 month - 1 day         
Day of Week                     |  DAYOFWEEK(), DAYNAME()                 |  DATENAME(), DATEPART(weekday, ...)     |  Not advisable               
Days Between Dates              |  DATEDIFF()                             |  DATEDIFF()                             |  Subtract integers (rare)    
Week Number                     |  WEEK()                                 |  DATEPART(week, ...)                    |  Divide day-of-year by 7     
Employees Joined Last 6 Months  |  DATE_SUB(CURDATE(), INTERVAL 6 MONTH)  |  DATEADD(month, -6, GETDATE())          |  Pre-calculate reference date
Employees Birthday This Month   |  MONTH(birth_date)                      |  MONTH(birth_date)                      |  Substring of date           
Generate All Dates in Range     |  Recursive CTE, helper table            |  Recursive CTE, helper table            |  Pre-generated list          
Age Calculation                 |  DATEDIFF(CURDATE(), birth_date)/365    |  DATEDIFF(year, birth_date, GETDATE())  |  Arithmetic year difference  
