"""Alternative API extraction and modeling patterns for comparison."""

from api_interview_lab.patterns.dataclass_pattern import extract_with_dataclasses
from api_interview_lab.patterns.pandas_pattern import extract_with_pandas
from api_interview_lab.patterns.pydantic_pattern import extract_with_pydantic
from api_interview_lab.patterns.typed_dict_pattern import extract_with_typed_dict

__all__ = [
    "extract_with_dataclasses",
    "extract_with_pandas",
    "extract_with_pydantic",
    "extract_with_typed_dict",
]
