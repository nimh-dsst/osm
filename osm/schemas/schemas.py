import base64
import datetime
from typing import Optional, Union

import pandas as pd
from odmantic import EmbeddedModel, Field, Model
from pydantic import EmailStr, field_serializer, field_validator, model_validator

from osm._utils import coerce_to_string

from .custom_fields import LongBytes
from .metrics_schemas import LLMExtractorMetrics, RtransparentMetrics


class Component(EmbeddedModel):
    model_config = {
        "extra": "forbid",
    }
    name: str
    version: str
    docker_image: Optional[str] = None
    docker_image_id: Optional[str] = None
    sample: Optional[LongBytes] = Field(
        default=b"",
        json_schema_extra={"exclude": True, "select": False, "write_only": True},
    )

    @field_serializer("sample")
    def serialize_longbytes(self, value: Optional[LongBytes]) -> Optional[str]:
        return base64.b64encode(value.get_value()).decode("utf-8") if value else None


class Client(EmbeddedModel):
    model_config = {"extra": "forbid"}
    compute_context_id: int
    email: Optional[EmailStr] = None


class Work(EmbeddedModel):
    """
    Unique reference for each publication/study/work. For each  “work”,
    pmid, doi (normalized), openalex ids are approaches to referencing such a
    study uniquely but any one of them may be used by a user. Versioning of the
    publications (as in pubmed vs Nature vs addendums) should all be handled
    naturally as part of an array of referenced “user input documents” (let’s say
    a pdf) provided as part of each "Invocation" or cli call.
    """

    model_config = {"extra": "forbid"}
    user_defined_id: Optional[str] = None
    pmid: Optional[int] = None
    doi: Optional[str] = None
    openalex_id: Optional[str] = None
    scopus_id: Optional[str] = None
    filename: str = ""
    content_hash: Optional[str] = None

    @field_validator("user_defined_id", mode="before")
    def fix_string(cls, v, *args, **kwargs):
        return coerce_to_string(v)

    @field_validator("pmid", mode="before")
    def handle_pd_na(cls, v, *args, **kwargs):
        return None if pd.isna(v) else v


class Invocation(Model):
    """
    Approximate document model. This may evolve but provides a starting point
    for the Odmantic document model used to interact with mongodb.
    """

    model_config = {"extra": "forbid"}
    metrics: Union[RtransparentMetrics, LLMExtractorMetrics]
    components: Optional[list[Component]] = []
    work: Work
    client: Client
    user_comment: str = ""
    osm_version: str
    funder: Optional[list[str]] = []
    data_tags: list[str] = []
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    @model_validator(pre=True)
    def validate_metrics(cls, values):
        metrics = values.get("metrics")
        if "metrics_group" not in metrics:
            raise ValueError("metrics field must contain a 'metrics_group' field")
        if metrics["metrics_group"] == "Rtransparent":
            values["metrics"] = RtransparentMetrics(**metrics)
        elif metrics["metrics_group"] == "LLMExtractor":
            values["metrics"] = LLMExtractorMetrics(**metrics)
        else:
            raise ValueError("Invalid 'metrics_group' in metrics")
        return values


class Quarantine(Model):
    payload: bytes = b""
    error_message: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class PayloadError(Model):
    error_message: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
