from typing import Optional

from odmantic import EmbeddedModel, Field
from pydantic import field_serializer, field_validator

from osm._utils import coerce_to_string

from .custom_fields import LongStr


#  The rtransparent tool can extract from parsed pdfs or from XML directly from pubmed central. The latter has many more fields.
#  all_indicators.csv from the rtransparent publication has both but has the following extra fields:
# code_text,com_code,com_data_availibility,com_file_formats,com_general_db,com_github_data,com_specific_db,com_suppl_code,com_supplemental_data,data_text,dataset,eigenfactor_score,field,is_art,is_code_pred,is_data_pred,is_relevant_code,is_relevant_data,jif,n_cite,score,year,
class RtransparentMetrics(EmbeddedModel):
    metrics_group: str = "RtransparentMetrics"
    # Mandatory fields
    is_open_code: Optional[bool]
    is_open_data: Optional[bool]

    # Optional fields
    year: Optional[int] = None
    filename: Optional[str] = None
    pmcid_pmc: Optional[int] = None
    pmid: Optional[int] = None
    doi: Optional[str] = None
    year_epub: Optional[int] = None
    year_ppub: Optional[int] = None
    journal: Optional[str] = None
    publisher: Optional[str] = None
    affiliation_country: Optional[str] = None
    affiliation_institution: Optional[str] = None
    type: Optional[str] = None
    data_text: Optional[LongStr] = None
    is_relevant_data: Optional[bool] = None
    com_specific_db: Optional[str] = None
    com_general_db: Optional[str] = None
    com_github_data: Optional[str] = None
    dataset: Optional[str] = None
    com_file_formats: Optional[str] = None
    com_supplemental_data: Optional[str] = None
    com_data_availibility: Optional[str] = None
    code_text: Optional[LongStr] = None
    is_relevant_code: Optional[bool] = None
    com_code: Optional[str] = None
    com_suppl_code: Optional[str] = None
    is_coi_pred: Optional[bool] = None
    coi_text: Optional[LongStr] = None
    is_coi_pmc_fn: Optional[bool] = None
    is_coi_pmc_title: Optional[bool] = None
    is_relevant_coi: Optional[bool] = None
    is_relevant_coi_hi: Optional[bool] = None
    is_relevant_coi_lo: Optional[bool] = None
    is_explicit_coi: Optional[bool] = None
    coi_1: Optional[bool] = None
    coi_2: Optional[bool] = None
    coi_disclosure_1: Optional[bool] = None
    commercial_1: Optional[bool] = None
    benefit_1: Optional[bool] = None
    consultant_1: Optional[bool] = None
    grants_1: Optional[bool] = None
    brief_1: Optional[bool] = None
    fees_1: Optional[bool] = None
    consults_1: Optional[bool] = None
    connect_1: Optional[bool] = None
    connect_2: Optional[bool] = None
    commercial_ack_1: Optional[bool] = None
    rights_1: Optional[bool] = None
    founder_1: Optional[bool] = None
    advisor_1: Optional[bool] = None
    paid_1: Optional[bool] = None
    board_1: Optional[bool] = None
    no_coi_1: Optional[bool] = None
    no_funder_role_1: Optional[bool] = None
    fund_text: Optional[LongStr] = None
    fund_pmc_institute: Optional[str] = None
    fund_pmc_source: Optional[str] = None
    fund_pmc_anysource: Optional[str] = None
    is_fund_pmc_group: Optional[bool] = None
    is_fund_pmc_title: Optional[bool] = None
    is_fund_pmc_anysource: Optional[bool] = None
    is_relevant_fund: Optional[bool] = None
    is_explicit_fund: Optional[bool] = None
    support_1: Optional[bool] = None
    support_3: Optional[bool] = None
    support_4: Optional[bool] = None
    support_5: Optional[bool] = None
    support_6: Optional[bool] = None
    support_7: Optional[bool] = None
    support_8: Optional[bool] = None
    support_9: Optional[bool] = None
    support_10: Optional[bool] = None
    developed_1: Optional[bool] = None
    received_1: Optional[bool] = None
    received_2: Optional[bool] = None
    recipient_1: Optional[bool] = None
    authors_1: Optional[bool] = None
    authors_2: Optional[bool] = None
    thank_1: Optional[bool] = None
    thank_2: Optional[bool] = None
    fund_1: Optional[bool] = None
    fund_2: Optional[bool] = None
    fund_3: Optional[bool] = None
    supported_1: Optional[bool] = None
    financial_1: Optional[bool] = None
    financial_2: Optional[bool] = None
    financial_3: Optional[bool] = None
    grant_1: Optional[bool] = None
    french_1: Optional[bool] = None
    common_1: Optional[bool] = None
    common_2: Optional[bool] = None
    common_3: Optional[bool] = None
    common_4: Optional[bool] = None
    common_5: Optional[bool] = None
    acknow_1: Optional[bool] = None
    disclosure_1: Optional[bool] = None
    disclosure_2: Optional[bool] = None
    fund_ack: Optional[bool] = None
    project_ack: Optional[bool] = None
    is_register_pred: Optional[bool] = None
    register_text: Optional[LongStr] = None
    is_research: Optional[bool] = None
    is_review: Optional[bool] = None
    is_reg_pmc_title: Optional[bool] = None
    is_relevant_reg: Optional[bool] = None
    is_method: Optional[bool] = None
    is_NCT: Optional[bool] = None
    is_explicit_reg: Optional[bool] = None
    prospero_1: Optional[bool] = None
    registered_1: Optional[bool] = None
    registered_2: Optional[bool] = None
    registered_3: Optional[bool] = None
    registered_4: Optional[bool] = None
    registered_5: Optional[bool] = None
    not_registered_1: Optional[bool] = None
    registration_1: Optional[bool] = None
    registration_2: Optional[bool] = None
    registration_3: Optional[bool] = None
    registration_4: Optional[bool] = None
    registry_1: Optional[bool] = None
    reg_title_1: Optional[bool] = None
    reg_title_2: Optional[bool] = None
    reg_title_3: Optional[bool] = None
    reg_title_4: Optional[bool] = None
    funded_ct_1: Optional[bool] = None
    ct_2: Optional[bool] = None
    ct_3: Optional[bool] = None
    protocol_1: Optional[bool] = None
    is_success: Optional[bool] = None
    is_art: Optional[bool] = None
    field: Optional[str] = None
    score: Optional[float] = None
    jif: Optional[float] = None
    eigenfactor_score: Optional[float] = None
    n_cite: Optional[float] = None
    #  some extra fields
    affiliation_aff_id: Optional[str] = None
    affiliation_all: Optional[str] = None
    article: Optional[str] = None
    author: Optional[str] = None
    author_aff_id: Optional[str] = None
    correspondence: Optional[str] = None
    date_epub: Optional[str] = None
    date_ppub: Optional[str] = None
    funding_text: Optional[LongStr] = None
    is_explicit: Optional[bool] = None
    is_fund_pred: Optional[bool] = None
    is_funded_pred: Optional[bool] = None
    is_relevant: Optional[bool] = None
    is_supplement: Optional[bool] = None
    issn_epub: Optional[str] = None
    issn_ppub: Optional[str] = None
    journal_iso: Optional[str] = None
    journal_nlm: Optional[str] = None
    license: Optional[str] = None
    n_affiliation: Optional[str] = None
    n_auth: Optional[str] = None
    n_fig_body: Optional[str] = None
    n_fig_floats: Optional[str] = None
    n_ref: Optional[str] = None
    n_table_body: Optional[str] = None
    n_table_floats: Optional[str] = None
    open_code_statements: Optional[LongStr] = None
    open_data_category: Optional[LongStr] = None
    open_data_statements: Optional[LongStr] = None
    pii: Optional[str] = None
    pmcid_uid: Optional[str] = None
    publisher_id: Optional[str] = None
    subject: Optional[str] = None
    title: Optional[str] = None
    is_data_pred: Optional[bool] = None
    is_code_pred: Optional[bool] = None

    @field_validator("article")
    def fix_string(cls, v):
        return coerce_to_string(v)

    @field_serializer(
        "data_text",
        "code_text",
        "coi_text",
        "fund_text",
        "register_text",
        "funding_text",
        "open_code_statements",
        "open_data_category",
        "open_data_statements",
    )
    def serialize_longstr(self, value: Optional[LongStr]) -> Optional[str]:
        return value.get_value() if value else None


class LLMExtractorMetrics(EmbeddedModel):
    """
    Model for extracting information from scientific publications. These metrics
    are a summary of the publications adherence to transparent or open
    scientific practices.
    Many unavailable identifiers (PMID, PMCID etc) can be found using pubmed: https://pubmed.ncbi.nlm.nih.gov/advanced/
    """

    metrics_group: str = "LLMExtractorMetrics"

    llm_model: str = Field(
        description="Exact verion of the llm model used to generate the data (not in publication itself but known by the model) e.g. GPT_4o_2024_08_06"
    )
    year: int = Field(
        description="Best attempt at extracting the year of the publication",
    )
    journal: str = Field(description="The journal in which the paper was published")
    article_type: list[str] = Field(
        description="The type of article e.g. research article, review, erratum, meta-analysis etc.",
    )
    country: list[str] = Field(
        description="The countries of the affiliations of the authors",
    )
    institute: list[str] = Field(
        description="The institutes of the affiliations of the authors",
    )
    doi: str = Field(description="The DOI of the paper")
    pmid: int = Field(
        description="The PMID of the paper, use '0' if one cannot be found"
    )
    pmcid: str = Field(
        description="The PMCID of the paper, use '0' if one cannot be found"
    )
    title: str = Field(description="The title of the paper")
    authors: list[str] = Field(description="The authors of the paper")
    publisher: str = Field(description="The publisher of the paper")
    is_open_code: bool = Field(
        description="Whether there is evidence that the code used for analysis in the paper has been shared online",
    )
    code_sharing_statement: list[str] = Field(
        description="The statement in the paper that indicates whether the code used for analysis has been shared online",
    )
    is_open_data: bool = Field(
        description="Whether there is evidence that the data used for analysis in the paper has been shared online",
    )
    data_sharing_statement: list[str] = Field(
        description="The statement in the paper that indicates whether the data used for analysis has been shared online",
    )
    data_repository_url: str = Field(
        description="The URL of the repository where the data can be found"
    )
    dataset_unique_identifier: list[str] = Field(
        description="Any unique identifiers the dataset may have"
    )
    code_repository_url: str = Field(
        description="The URL of the repository where the code and data can be found"
    )
    has_coi_statement: bool = Field(
        description="Whether there is a conflict of interest statement in the paper",
    )
    coi_statement: list[str] = Field(
        description="The conflict of interest statement in the paper"
    )
    funder: list[str] = Field(
        description="The funders of the research, may contain multiple funders",
    )
    has_funding_statement: bool = Field(
        description="Whether there is a funding statement in the paper"
    )
    funding_statement: list[str] = Field(
        description="The funding statement in the paper"
    )
    has_registration_statement: bool = Field(
        description="Whether there is a registration statement in the paper",
    )
    registration_statement: list[str] = Field(
        description="The registration statement in the paper"
    )
    reasoning_steps: list[str] = Field(
        description="The reasoning steps used to extract the information from the paper",
    )
