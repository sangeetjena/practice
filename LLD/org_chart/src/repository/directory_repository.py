from abc import ABC, abstractmethod

from models.datamodel import Employee, Group


class DirectoryRepository(ABC):
    @abstractmethod
    def add_group(self, group: Group) -> None: ...
    @abstractmethod
    def save_group(self, group: Group) -> None: ...
    @abstractmethod
    def get_group(self, group_id: int) -> Group | None: ...
    @abstractmethod
    def add_employee(self, employee: Employee) -> None: ...
    @abstractmethod
    def save_employee(self, employee: Employee) -> None: ...
    @abstractmethod
    def get_employee(self, employee_id: int) -> Employee | None: ...


class InMemoryDirectoryRepository(DirectoryRepository):
    def __init__(self) -> None:
        self.groups: dict[int, Group] = {}
        self.employees: dict[int, Employee] = {}

    def add_group(self, group: Group) -> None:
        self.groups[group.group_id] = group

    def save_group(self, group: Group) -> None:
        self.groups[group.group_id] = group

    def get_group(self, group_id: int) -> Group | None:
        return self.groups.get(group_id)

    def add_employee(self, employee: Employee) -> None:
        self.employees[employee.employee_id] = employee

    def save_employee(self, employee: Employee) -> None:
        self.employees[employee.employee_id] = employee

    def get_employee(self, employee_id: int) -> Employee | None:
        return self.employees.get(employee_id)

