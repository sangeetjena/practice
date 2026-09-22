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
        self._repository = repository
        self._lock = RLock()

    def add_group(self, group: Group) -> None:
        with self._lock:
            if self._repository.get_group(group.group_id):
                raise AlreadyExistsError(f"Group {group.group_id} already exists")
            if group.parent_group_id is not None:
                self._require_group(group.parent_group_id)
            self._repository.add_group(group)
            logger.info("Added group id=%s parent=%s", group.group_id, group.parent_group_id)

    def add_employee(self, employee: Employee) -> None:
        with self._lock:
            if self._repository.get_employee(employee.employee_id):
                raise AlreadyExistsError(
                    f"Employee {employee.employee_id} already exists"
                )
            self._require_group(employee.group_id)
            self._repository.add_employee(employee)
            logger.info("Added employee id=%s group=%s", employee.employee_id, employee.group_id)

    def move_employee(self, employee_id: int, new_group_id: int) -> None:
        with self._lock:
            employee = self._require_employee(employee_id)
            self._require_group(new_group_id)
            self._repository.save_employee(
                replace(employee, group_id=new_group_id)
            )
            logger.info("Moved employee id=%s from=%s to=%s", employee_id, employee.group_id, new_group_id)

    def move_group(self, group_id: int, new_parent_id: int | None) -> None:
        with self._lock:
            group = self._require_group(group_id)
            if new_parent_id is not None:
                self._require_group(new_parent_id)
                self._ensure_move_has_no_cycle(group_id, new_parent_id)
            self._repository.save_group(
                replace(group, parent_group_id=new_parent_id)
            )
            logger.info("Moved group id=%s from=%s to=%s", group_id, group.parent_group_id, new_parent_id)

    def closest_common_group(self, employee_ids: list[int]) -> Group:
        if not employee_ids:
            raise InvalidInputError("At least one employee ID is required")

        with self._lock:
            group_ids = [
                self._require_employee(employee_id).group_id
                for employee_id in employee_ids
            ]
            first_path = self._ancestor_path(group_ids[0])
            other_ancestors = [
                set(self._ancestor_path(group_id)) for group_id in group_ids[1:]
            ]

            for group_id in first_path:
                if all(group_id in ancestors for ancestors in other_ancestors):
                    return self._require_group(group_id)

            raise NoCommonGroupError("Employees belong to separate group trees")

    def get_employee(self, employee_id: int) -> Employee:
        with self._lock:
            return self._require_employee(employee_id)

    def _ancestor_path(self, group_id: int) -> list[int]:
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
        if group_id in self._ancestor_path(new_parent_id):
            raise InvalidHierarchyError(
                f"Moving group {group_id} under {new_parent_id} creates a cycle"
            )

    def _require_group(self, group_id: int) -> Group:
        group = self._repository.get_group(group_id)
        if group is None:
            raise NotFoundError(f"Group {group_id} was not found")
        return group

    def _require_employee(self, employee_id: int) -> Employee:
        employee = self._repository.get_employee(employee_id)
        if employee is None:
            raise NotFoundError(f"Employee {employee_id} was not found")
        return employee


