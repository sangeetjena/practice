class DirectoryError(Exception):
    """Base for expected domain failures; handled at the application boundary."""

    code = "directory_error"


class AlreadyExistsError(DirectoryError):
    code = "already_exists"


class NotFoundError(DirectoryError):
    code = "not_found"


class InvalidHierarchyError(DirectoryError):
    code = "invalid_hierarchy"


class NoCommonGroupError(DirectoryError):
    code = "no_common_group"


class InvalidInputError(DirectoryError):
    code = "invalid_input"
