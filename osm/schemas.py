from typing import Optional

from odmantic import EmbeddedModel, Model

# mriqc applies a unique id to each person so that you can aggregate and detect
# duplication. One can have different views of same work
# (pubmedcentral and nature). Each would have different filenames, different
# provenance, different md5sum. Usually there is a final version of record,
# ideally we would be analysing that. Generally for high throughput we analyse
# the open access pubmed central.


# class Work(EmbeddedModel):
#     """
#     Unique reference for each publication/study/work. For each  “work”,
#     pmid, doi (normalized), openalex ids are approaches to referencing such a
#     study uniquely but any one of them may be used by a user. Versioning of the
#     publications (as in pubmed vs Nature vs addendums) should all be handled
#     naturally as part of an array of referenced “user input documents” (let’s say
#     a pdf) provided as part of each "Invocation" or cli call.
#     """

#     user_defined_id: str
#     pmid: str
#     doi: str
#     openalex_id: str
#     scopus_id: str
#     file: bytes
#     content_hash: str
#     timestamp: str  # can be inferred from objectid


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

    component_id: str
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
    compute_context_id: str
    # email: EmailStr
    invocation_id: str


# class Workflow(EmbeddedModel):
#     """
#     Schema to describe an analysis that was run by a user. This represents a
#     chain of steps that culminate in the bibliometric output json. It will
#     contain a reference to the primary document of the "work" supplied as input,
#     the steps run, and derivatives created.
#     """
#     output: Metrics
#     work_id: str
#     steps: list[Component]
#     derivatives_created: list[Derivative]


class Work(Model):
    # TODO: condense ids into a single field with validation
    user_defined_id: str
    pmid: Optional[str] = None
    doi: Optional[str] = None
    openalex_id: Optional[str] = None
    scopus_id: Optional[str] = None
    # file: bytes
    content_hash: str


class Invocation(Model):
    """
    Approximate document model. This may evolve but provides a starting point
    for the Odmantic document model used to interact with mongodb.
    """

    osm_version: str
    user_comment: str
    # timestamp: str
    # client: Client = Reference()
    # work: Work = Reference()
    # workflow: Workflow
    # metrics: dict


# class Invocation(Model):
#     osm_version: str
#     timestamp: str
#     user_comment:Optional[str] = None
#     work: Work = Reference()


# class WorkPayload(Model):
#     user_defined_id: str
#     pmid:Optional[str] = None
#     doi:Optional[str] = None
#     openalex_id:Optional[str] = None
#     scopus_id:Optional[str] = None
#     file: bytes
#     content_hash: str
#     timestamp: str

# class InvocationPayload(Model):
#     osm_version: str
#     timestamp: str
#     user_comment:Optional[str] = None
#     work: WorkPayload

# class Rtransparent(Component):
#     name: str = "rtransparent"
#     version: 0.13
#     docker_image: "nimh-dsst/rtransparent:0.13"
#     docker_image_id: "dsjfkldsjflkdsjlf2jkl23j"

# class ScibeamParser(Component):
#     name: str = "rtransparent"
#     version: "0.5.1"
#     docker_image: "elife/scibeam-parser:0.5.1"
#     docker_image_id: "dsjfkldsjflkdsjlf2jkl23j"
