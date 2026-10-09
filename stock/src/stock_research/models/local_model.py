"""Agent-readable tool schemas: validation and field descriptions are runtime contracts."""

from typing import Annotated

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints

Symbol = Annotated[
    str, StringConstraints(strip_whitespace=True, to_upper=True, pattern=r"^[A-Za-z0-9.^-]{1,24}$")
]


class FeatureSnapshot(BaseModel):
    symbol: Symbol
    cutoff_at: AwareDatetime
    feature_version: str = Field(
        description="Must match the deployed model's feature contract, e.g. daily-v1."
    )
    features: dict[str, float] = Field(
        description="Versioned model features supplied by ML_INFRA or a test fixture, not invented by an agent."
    )
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class PredictInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    symbol: Symbol
    snapshot: FeatureSnapshot | None = Field(
        default=None,
        description="Pass an explicit snapshot to bypass the server's DB-backed /features endpoint.",
    )
    latest_cutoff: AwareDatetime | None = Field(
        default=None,
        description="Reject model features observed after the workflow's evidence cutoff.",
    )
    allow_feature_fetch: bool = Field(
        default=True, description="False in DB-free development: only POST /predict is permitted."
    )


class ModelPrediction(BaseModel):
    model_name: str
    model_version: str
    target: str
    probability_up: float = Field(ge=0, le=1)
    feature_version: str | None = None


class PredictOutput(BaseModel):
    snapshot: FeatureSnapshot
    prediction: ModelPrediction
