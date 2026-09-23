from abc import ABC, abstractmethod

from models.datamodel import Employee, Group


class DirectoryRepository(ABC):
    @abstractmethod
    def add_group(self, group: Group) -> None:
        """Store a group by ID; service owns duplicate validation.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: None.
        Example: repository.add_group(group) stores the supplied immutable model.
        """
        ...

    @abstractmethod
    def save_group(self, group: Group) -> None:
        """Write a replacement group by ID; service validates the update.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: None.
        Example: repository.save_group(group) stores the supplied immutable model.
        """
        ...

    @abstractmethod
    def get_group(self, group_id: int) -> Group | None:
        """Look up a group by ID without applying service-level errors.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: Group or None when absent.
        Example: repository.get_group(999) returns None when absent.
        """
        ...

    @abstractmethod
    def add_employee(self, employee: Employee) -> None:
        """Store a employee by ID; service owns duplicate validation.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: None.
        Example: repository.add_employee(employee) stores the supplied immutable model.
        """
        ...

    @abstractmethod
    def save_employee(self, employee: Employee) -> None:
        """Write a replacement employee by ID; service validates the update.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: None.
        Example: repository.save_employee(employee) stores the supplied immutable model.
        """
        ...

    @abstractmethod
    def get_employee(self, employee_id: int) -> Employee | None:
        """Look up a employee by ID without applying service-level errors.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: Employee or None when absent.
        Example: repository.get_employee(999) returns None when absent.
        """
        ...


class InMemoryDirectoryRepository(DirectoryRepository):
    def __init__(self) -> None:
        """Create empty group and employee dictionaries.

        Called by: Application startup before injecting the repository into one service.
        Returns: None; construction produces a repository.
        Example: InMemoryDirectoryRepository().get_group(1) returns None.
        """
        self.groups: dict[int, Group] = {}
        self.employees: dict[int, Employee] = {}

    def add_group(self, group: Group) -> None:
        """Store a group by ID; service owns duplicate validation.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: None.
        Example: repository.add_group(group) stores the supplied immutable model.
        """
        self.groups[group.group_id] = group

    def save_group(self, group: Group) -> None:
        """Write a replacement group by ID; service validates the update.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: None.
        Example: repository.save_group(group) stores the supplied immutable model.
        """
        self.groups[group.group_id] = group

    def get_group(self, group_id: int) -> Group | None:
        """Look up a group by ID without applying service-level errors.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: Group or None when absent.
        Example: repository.get_group(999) returns None when absent.
        """
        return self.groups.get(group_id)

    def add_employee(self, employee: Employee) -> None:
        """Store a employee by ID; service owns duplicate validation.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: None.
        Example: repository.add_employee(employee) stores the supplied immutable model.
        """
        self.employees[employee.employee_id] = employee

    def save_employee(self, employee: Employee) -> None:
        """Write a replacement employee by ID; service validates the update.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: None.
        Example: repository.save_employee(employee) stores the supplied immutable model.
        """
        self.employees[employee.employee_id] = employee

    def get_employee(self, employee_id: int) -> Employee | None:
        """Look up a employee by ID without applying service-level errors.

        Called by: OrganizationDirectory through its repository dependency; this method does not
        acquire a lock.
        Returns: Employee or None when absent.
        Example: repository.get_employee(999) returns None when absent.
        """
        return self.employees.get(employee_id)
