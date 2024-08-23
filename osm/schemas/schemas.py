import base64
from datetime import datetime
from typing import Optional

from odmantic import EmbeddedModel, Field, Model
from pydantic import EmailStr, field_validator

from .custom_fields import LongBytes
from .metrics_schemas import RtransparentMetrics


class Component(EmbeddedModel):
    model_config = {
        "extra": "forbid",
        "json_encoders": {
            LongBytes: lambda v: base64.b64encode(v.get_value()).decode("utf-8"),
        },
    }
    name: str
    version: str
    docker_image: Optional[str] = None
    docker_image_id: Optional[str] = None
    sample: Optional[LongBytes] = Field(
        default=b"",
        json_schema_extra={"exclude": True, "select": False, "write_only": True},
    )


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
    user_defined_id: str
    pmid: Optional[int] = None
    doi: Optional[str] = None
    openalex_id: Optional[str] = None
    scopus_id: Optional[str] = None
    filename: str = ""
    content_hash: Optional[str] = None

    @field_validator("user_defined_id")
    def coerce_to_string(cls, v):
        if isinstance(v, (int, float, bool)):
            return str(v)
        elif not isinstance(v, str):
            raise ValueError(
                "string required or a type that can be coerced to a string"
            )
        return v


class Invocation(Model):
    """
    Approximate document model. This may evolve but provides a starting point
    for the Odmantic document model used to interact with mongodb.
    """

    model_config = {"extra": "forbid"}
    metrics: RtransparentMetrics
    components: Optional[list[Component]] = None
    work: Work
    client: Client
    user_comment: str = ""
    osm_version: str
    funder: Optional[list[str]] = None
    data_tags: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
