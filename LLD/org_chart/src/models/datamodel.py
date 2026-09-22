from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Group:
    group_id: int
    name: str
    parent_group_id: int | None = None


@dataclass(frozen=True, slots=True)
class Employee:
    employee_id: int
    name: str
    group_id: int
    email: str | None = None
