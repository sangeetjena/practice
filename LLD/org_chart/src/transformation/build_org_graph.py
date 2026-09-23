import logging
from dataclasses import replace
from threading import RLock

from exceptions import (
    AlreadyExistsError,
    InvalidHierarchyError,
    InvalidInputError,
    NoCommonGroupError,
    NotFoundError,
)
from models.datamodel import Employee, Group
from repository import DirectoryRepository

logger = logging.getLogger(__name__)


class OrganizationDirectory:
    """Thread-safe application service for one company's group hierarchy."""

    def __init__(self, repository: DirectoryRepository) -> None:
        """Inject a repository and create one service-instance lock.

        Called by: Application startup and test fixtures.
        Returns: None; construction produces OrganizationDirectory.
        Example: OrganizationDirectory(InMemoryDirectoryRepository()) creates an empty directory.
        """
        self._repository = repository
        self._lock = RLock()

    def add_group(self, group: Group) -> None:
        """Insert a new group after checking identity and parent existence.

        Called by: Application setup or group-creation caller.
        Returns: None; duplicate/missing-parent errors leave state unchanged.
        Example: directory.add_group(Group(1, "Company")) creates a root.
        """
        with self._lock:
            if self._repository.get_group(group.group_id):
                raise AlreadyExistsError(f"Group {group.group_id} already exists")
            if group.parent_group_id is not None:
                self._require_group(group.parent_group_id)
            self._repository.add_group(group)
            logger.info("Added group id=%s parent=%s", group.group_id, group.parent_group_id)

    def add_employee(self, employee: Employee) -> None:
        """Insert an employee after checking identity and membership group.

        Called by: Employee-creation caller.
        Returns: None; duplicate or missing group raises.
        Example: With group 1 present, add_employee(Employee(101, "Alice", 1)) succeeds.
        """
        with self._lock:
            if self._repository.get_employee(employee.employee_id):
                raise AlreadyExistsError(f"Employee {employee.employee_id} already exists")
            self._require_group(employee.group_id)
            self._repository.add_employee(employee)
            logger.info("Added employee id=%s group=%s", employee.employee_id, employee.group_id)

    def move_employee(self, employee_id: int, new_group_id: int) -> None:
        """Replace an employee's membership after validating the destination.

        Called by: Organization-edit caller.
        Returns: None; other employee fields are preserved.
        Example: directory.move_employee(101, 2) moves employee 101 to existing group 2.
        """
        with self._lock:
            employee = self._require_employee(employee_id)
            self._require_group(new_group_id)
            self._repository.save_employee(replace(employee, group_id=new_group_id))
            logger.info(
                "Moved employee id=%s from=%s to=%s", employee_id, employee.group_id, new_group_id
            )

    def move_group(self, group_id: int, new_parent_id: int | None) -> None:
        """Change a group's parent while rejecting cycles.

        Called by: Organization-edit caller.
        Returns: None; invalid moves raise without mutation.
        Example: directory.move_group(3, 2) puts group 3 under existing group 2.
        """
        with self._lock:
            group = self._require_group(group_id)
            if new_parent_id is not None:
                self._require_group(new_parent_id)
                self._ensure_move_has_no_cycle(group_id, new_parent_id)
            self._repository.save_group(replace(group, parent_group_id=new_parent_id))
            logger.info(
                "Moved group id=%s from=%s to=%s", group_id, group.parent_group_id, new_parent_id
            )

    def closest_common_group(self, employee_ids: list[int]) -> Group:
        """Walk ancestors to find the deepest group shared by all requested employees.

        Called by: Directory query caller and demo.
        Returns: Group; empty input, missing employees or disconnected trees raise.
        Example: Employees in Search and Data under Engineering return Engineering.
        """
        if not employee_ids:
            raise InvalidInputError("At least one employee ID is required")

        with self._lock:
            group_ids = [
                self._require_employee(employee_id).group_id for employee_id in employee_ids
            ]
            first_path = self._ancestor_path(group_ids[0])
            other_ancestors = [set(self._ancestor_path(group_id)) for group_id in group_ids[1:]]

            for group_id in first_path:
                if all(group_id in ancestors for ancestors in other_ancestors):
                    return self._require_group(group_id)

            raise NoCommonGroupError("Employees belong to separate group trees")

    def get_employee(self, employee_id: int) -> Employee:
        """Read one employee safely through the service lock.

        Called by: Directory query caller.
        Returns: Employee; missing identity raises NotFoundError.
        Example: directory.get_employee(101) returns Alice after she is added.
        """
        with self._lock:
            return self._require_employee(employee_id)

    def _ancestor_path(self, group_id: int) -> list[int]:
        """Walk parent links from a group to its root, detecting corrupt cycles.

        Called by: closest_common_group and move-cycle validation.
        Returns: List of IDs from nearest group to root.
        Example: For Search=3 under Engineering=2 under Company=1, returns [3, 2, 1].
        """
        path: list[int] = []
        visited: set[int] = set()
        current_id: int | None = group_id

        while current_id is not None:
            if current_id in visited:
                raise InvalidHierarchyError("Cycle found in group hierarchy")
            visited.add(current_id)
            path.append(current_id)
            current_id = self._require_group(current_id).parent_group_id

        return path

    def _ensure_move_has_no_cycle(self, group_id: int, new_parent_id: int) -> None:
        """Reject a proposed parent that is the group itself or its descendant.

        Called by: move_group under the service lock.
        Returns: None; a cycle raises InvalidHierarchyError.
        Example: Moving Engineering under its Search child is rejected.
        """
        if group_id in self._ancestor_path(new_parent_id):
            raise InvalidHierarchyError(
                f"Moving group {group_id} under {new_parent_id} creates a cycle"
            )

    def _require_group(self, group_id: int) -> Group:
        """Load an existing group or raise a domain error.

        Called by: Service validation and ancestor traversal.
        Returns: Group.
        Example: _require_group(999) raises NotFoundError when 999 is absent.
        """
        group = self._repository.get_group(group_id)
        if group is None:
            raise NotFoundError(f"Group {group_id} was not found")
        return group

    def _require_employee(self, employee_id: int) -> Employee:
        """Load an existing employee or raise a domain error.

        Called by: move_employee, get_employee and closest_common_group.
        Returns: Employee.
        Example: _require_employee(101) returns the stored employee when present.
        """
        employee = self._repository.get_employee(employee_id)
        if employee is None:
            raise NotFoundError(f"Employee {employee_id} was not found")
        return employee
