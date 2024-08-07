from typing import Optional

from odmantic import EmbeddedModel, Model
from pydantic import EmailStr

# mriqc applies a unique id to each person so that you can aggregate and detect
# duplication. One can have different views of same work
# (pubmedcentral and nature). Each would have different filenames, different
# provenance, different md5sum. Usually there is a final version of record,
# ideally we would be analysing that. Generally for high throughput we analyse
# the open access pubmed central.


class Derivative(EmbeddedModel):
    """
    Gridfs can avoid issues with size limitations. Each derivative is an output of the
    execution of a single container with the “preceding document” or “parent”
    referenced (this could be a primary document or another derivative). A primary
    document could have several different derivatives (scibeam and rtransparent outputs)
    and/or several versions of the same derivative type (scibeam and rtransparent
    across different releases or rtransparent or modifications of our docker
    image). A text label would be useful here but a docker image id is likely the
    sanest way to track derivatives (which would mean that all derivatives must be
    computed in a docker container).
    """

    text_label: str
    version: str


class Component(EmbeddedModel):
    name: str
    version: str
    docker_image: str
    docker_image_id: str


class Metrics(EmbeddedModel):
    """Potentially link to other databases for extra metadata"""

    metrics: dict


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
    filename: str
    file: Optional[str] = None
    content_hash: Optional[str] = None


class Invocation(Model):
    """
    Approximate document model. This may evolve but provides a starting point
    for the Odmantic document model used to interact with mongodb.
    """

    osm_version: str
    user_comment: Optional[str]
    client: Client
    work: Work
    metrics: dict
    # derivatives: list[Derivative]
    # components: list[Component]


# Rtransparent: Component.construct(name="rtransparent", version="0.13", docker_image="nimh-dsst/rtransparent:0.13",
# docker_image_id="dsjfkldsjflkdsjlf2jkl23j") Derivative.construct(name="rtransparent", version="0.13",
# docker_image="nimh-dsst/rtransparent:0.13", docker_image_id="dsjfkldsjflkdsjlf2jkl23j") ScibeamParser:
# Component.construct(name="scibeam-parser", version="0.5.1", docker_image="elife/scibeam-parser:0.5.1",
# docker_image_id="dsjfkldsjflkdsjlf2jkl23j")
