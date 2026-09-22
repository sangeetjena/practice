import pytest

from exceptions import (
    AlreadyExistsError,
    InvalidHierarchyError,
    InvalidInputError,
    NoCommonGroupError,
    NotFoundError,
)
from models.datamodel import Employee, Group
from repository import InMemoryDirectoryRepository
from transformation.build_org_graph import OrganizationDirectory


@pytest.fixture
def directory() -> OrganizationDirectory:
    service = OrganizationDirectory(InMemoryDirectoryRepository())
    service.add_group(Group(1, "Company"))
    service.add_group(Group(2, "Engineering", 1))
    service.add_group(Group(3, "Search", 2))
    service.add_group(Group(4, "Data", 2))
    service.add_group(Group(5, "SRE", 1))
    service.add_employee(Employee(101, "Alice", 3))
    service.add_employee(Employee(102, "Bob", 4))
    service.add_employee(Employee(103, "Carol", 3))
    return service


def test_employees_in_same_group(directory: OrganizationDirectory) -> None:
    assert directory.closest_common_group([101, 103]).group_id == 3


def test_employees_in_sibling_groups(directory: OrganizationDirectory) -> None:
    assert directory.closest_common_group([101, 102]).group_id == 2


def test_single_employee_returns_own_group(directory: OrganizationDirectory) -> None:
    assert directory.closest_common_group([101]).group_id == 3


def test_employee_move_changes_result(directory: OrganizationDirectory) -> None:
    directory.move_employee(102, 5)
    assert directory.closest_common_group([101, 102]).group_id == 1
    assert directory.get_employee(102).group_id == 5


def test_group_move_changes_result(directory: OrganizationDirectory) -> None:
    directory.move_group(4, 5)
    assert directory.closest_common_group([101, 102]).group_id == 1


def test_group_move_rejects_cycle(directory: OrganizationDirectory) -> None:
    with pytest.raises(InvalidHierarchyError):
        directory.move_group(2, 3)


def test_empty_employee_list_is_rejected(directory: OrganizationDirectory) -> None:
    with pytest.raises(InvalidInputError):
        directory.closest_common_group([])


def test_unknown_employee_is_rejected(directory: OrganizationDirectory) -> None:
    with pytest.raises(NotFoundError):
        directory.closest_common_group([999])


def test_unknown_parent_is_rejected(directory: OrganizationDirectory) -> None:
    with pytest.raises(NotFoundError):
        directory.add_group(Group(10, "Unknown child", 999))


def test_duplicate_employee_is_rejected(directory: OrganizationDirectory) -> None:
    with pytest.raises(AlreadyExistsError):
        directory.add_employee(Employee(101, "Duplicate", 3))


def test_separate_trees_have_no_common_group(
    directory: OrganizationDirectory,
) -> None:
    directory.add_group(Group(10, "Another company"))
    directory.add_employee(Employee(104, "Dan", 10))

    with pytest.raises(NoCommonGroupError):
        directory.closest_common_group([101, 104])


def test_parallel_employee_adds_are_safe(
    directory: OrganizationDirectory,
) -> None:
    from concurrent.futures import ThreadPoolExecutor

    def add(employee_id: int) -> None:
        directory.add_employee(Employee(employee_id, f"E{employee_id}", 3))

    employee_ids = list(range(200, 250))
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(add, employee_ids))

    assert all(
        directory.get_employee(employee_id).employee_id == employee_id
        for employee_id in employee_ids
    )



def test_repository_contract_rejects_incomplete_implementation() -> None:
    from repository import DirectoryRepository

    class IncompleteRepository(DirectoryRepository):
        pass

    with pytest.raises(TypeError):
        IncompleteRepository()


def test_domain_error_has_stable_code(directory) -> None:
    from exceptions import DirectoryError

    with pytest.raises(DirectoryError) as caught:
        directory.get_employee(999)
    assert caught.value.code == "not_found"


def test_successful_move_logs_ids_without_personal_details(directory, caplog) -> None:
    import logging

    with caplog.at_level(logging.INFO):
        directory.move_employee(101, 4)

    assert "Moved employee id=101 from=3 to=4" in caplog.text
    assert "Alice" not in caplog.text


def test_failed_move_preserves_state_and_has_no_success_log(directory, caplog) -> None:
    import logging

    with caplog.at_level(logging.INFO), pytest.raises(NotFoundError):
        directory.move_employee(101, 999)

    assert directory.get_employee(101).group_id == 3
    assert "Moved employee" not in caplog.text
