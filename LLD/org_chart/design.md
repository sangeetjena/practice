Emp grouping service:

entityes:
    organization:
        org:
            employee 


Company:
    [org]

org:
    orgid: str
    employee: list(employee_id)   [optional ]
    parent_org_id: str

employee:
    employee_id: str
    org_id: str
    employee_name: str
    employee_details: dict


example:
    org: [org(org1,["002","0023"], "001" ),
         org(org3,["002","0023"], "001" ),
         org(org4,["002","0023"], "003" )]

    
    emplployee:
    {"emp1": employee("emp1", 001, {}),
     "emp2": employee("emp1", 001, {}),
    "emp3": employee("emp1", 002, {})
    }



algorithm:
DFS:
    emp1: sales -> eng -> company
    emp2: data -> eng -> company

company:
    eng:
        sales::
            emp1
        data:
            emp2
            emp3
        search
            emp4
    sre:
        search::    
            emp5