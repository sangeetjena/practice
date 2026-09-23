import logging

from exceptions import DirectoryError
from log import configure_logging
from models.datamodel import Employee, Group
from repository import InMemoryDirectoryRepository
from transformation.build_org_graph import OrganizationDirectory


def main() -> None:
    """Run the org_chart demonstration using local objects.

    Called by: the script entry point.
    Returns: None; prints sample operation results.
    Example: python src/main.py from the project directory.
    """
    directory = OrganizationDirectory(InMemoryDirectoryRepository())

    directory.add_group(Group(1, "Company"))
    directory.add_group(Group(2, "Engineering", 1))
    directory.add_group(Group(3, "Search", 2))
    directory.add_group(Group(4, "Data", 2))

    directory.add_employee(Employee(101, "Alice", 3))
    directory.add_employee(Employee(102, "Bob", 4))

    common = directory.closest_common_group([101, 102])
    print(f"Closest common group: {common.name}")


if __name__ == "__main__":
    configure_logging()
    try:
        main()
    except DirectoryError as error:
        logging.getLogger(__name__).warning("%s: %s", error.code, error)
        raise SystemExit(1) from error
