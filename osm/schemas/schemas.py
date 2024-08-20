from typing import Optional

from odmantic import EmbeddedModel, Model
from pydantic import EmailStr

from .metrics_schemas import RtransparentMetrics


class Component(EmbeddedModel):
    name: str
    version: str
    docker_image: Optional[str] = None
    docker_image_id: Optional[str] = None


class Client(EmbeddedModel):
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

    user_defined_id: str
    pmid: Optional[str] = None
    doi: Optional[str] = None
    openalex_id: Optional[str] = None
    scopus_id: Optional[str] = None
    filename: str = ""
    file: Optional[str] = None
    content_hash: Optional[str] = None


class Invocation(Model):
    """
    Approximate document model. This may evolve but provides a starting point
    for the Odmantic document model used to interact with mongodb.
    """

    work: Work
    metrics: RtransparentMetrics

    components: list[Component]
    client: Client
    user_comment: Optional[str] = ""
    osm_version: str
    # Potentially link to other databases for extra metadata but for now will just use component outputs


# Rtransparent: Component.construct(name="rtransparent", version="0.13", docker_image="nimh-dsst/rtransparent:0.13", docker_image_id="dsjfkldsjflkdsjlf2jkl23j")
# ScibeamParser: Component.construct(name="scibeam-parser", version="0.5.1", docker_image="elife/scibeam-parser:0.5.1",docker_image_id="dsjfkldsjflkdsjlf2jkl23j")
