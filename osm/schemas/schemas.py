import base64
import datetime
from typing import Annotated, Optional, Union

import pandas as pd
from bson import ObjectId
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from osm._utils import coerce_to_string

from .custom_fields import LongBytes
from .metrics_schemas import (
    LLMExtractorMetrics,
    ManualAnnotationNIMHDSST,
    RtransparentMetrics,
)

PyObjectId = Annotated[str, BeforeValidator(str)]


class Component(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    version: str
    docker_image: str | None = None
    docker_image_id: Union[str, None] = None
    sample: Union[LongBytes, None] = Field(
        default=b"", exclude=True, description="Serialized to base64 string"
    )

    @staticmethod
    def serialize_longbytes(value: LongBytes) -> Union[str, None]:
        return base64.b64encode(value.get_value()).decode("utf-8") if value else None

    def bson(self):
        """Custom BSON serialization to handle LongBytes."""
        data = self.model_dump()
        if self.sample:
            data["sample"] = self.serialize_longbytes(self.sample)
        return data


class Client(BaseModel):
    model_config = {"extra": "forbid"}
    compute_context_id: int
    email: Optional[EmailStr] = None


class Work(BaseModel):
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


class Invocation(BaseModel):
    """
    Approximate document model. This may evolve but provides a starting point
    for the document model used to interact with mongodb.
    """

    model_config = {"extra": "forbid"}
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    manual_annotation_nimhdsst: Optional[ManualAnnotationNIMHDSST] = Field(default=None)
    llm_extractor_metrics: Optional[LLMExtractorMetrics] = Field(default=None)
    rtransparent_metrics: Optional[RtransparentMetrics] = Field(default=None)
    components: Optional[list[Component]] = []
    work: Work
    client: Client
    user_comment: Optional[str] = None
    osm_version: Optional[str] = None
    funder: Optional[list[str]] = []
    data_tags: list[str] = []
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC).replace(
            microsecond=0
        )
    )
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime.datetime: lambda dt: dt.isoformat(), ObjectId: str},
    )
    # class Settings:
    #     keep_nulls = False
    #     populate_by_name = True


class Quarantine(BaseModel):
    payload: bytes = b""
    error_message: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC).replace(
            microsecond=0
        )
    )

    class Settings:
        keep_nulls = False
        populate_by_name = True


class PayloadError(BaseModel):
    error_message: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC).replace(
            microsecond=0
        )
    )

    class Settings:
        keep_nulls = False
        populate_by_name = True
