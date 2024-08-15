from typing import Optional

from odmantic import EmbeddedModel


class RtransparentMetrics(EmbeddedModel):
    pmcid_pmc: Optional[int] = None
    pmid: Optional[int] = None
    doi: Optional[str] = None
    filename: Optional[str] = None
    year: Optional[int] = None
    year_epub: Optional[int] = None
    year_ppub: Optional[int] = None
    journal: Optional[str] = None
    publisher: Optional[str] = None
    affiliation_country: Optional[str] = None
    affiliation_institution: Optional[str] = None
    type: Optional[str] = None
    is_data_pred: Optional[bool] = None
    data_text: Optional[str] = None
    is_relevant_data: Optional[bool] = None
    com_specific_db: Optional[str] = None
    com_general_db: Optional[str] = None
    com_github_data: Optional[str] = None
    dataset: Optional[str] = None
    com_file_formats: Optional[str] = None
    com_supplemental_data: Optional[str] = None
    com_data_availibility: Optional[str] = None
    is_code_pred: Optional[bool] = None
    code_text: Optional[str] = None
    is_relevant_code: Optional[bool] = None
    com_code: Optional[str] = None
    com_suppl_code: Optional[str] = None
    is_coi_pred: Optional[bool] = None
    coi_text: Optional[str] = None
    is_coi_pmc_fn: Optional[bool] = None
    is_coi_pmc_title: Optional[str] = None
    is_relevant_coi: Optional[str] = None
    is_relevant_coi_hi: Optional[str] = None
    is_relevant_coi_lo: Optional[str] = None
    is_explicit_coi: Optional[str] = None
    coi_1: Optional[str] = None
    coi_2: Optional[str] = None
    coi_disclosure_1: Optional[str] = None
    commercial_1: Optional[str] = None
    benefit_1: Optional[str] = None
    consultant_1: Optional[str] = None
    grants_1: Optional[str] = None
    brief_1: Optional[str] = None
    fees_1: Optional[str] = None
    consults_1: Optional[str] = None
    connect_1: Optional[str] = None
    connect_2: Optional[str] = None
    commercial_ack_1: Optional[str] = None
    rights_1: Optional[str] = None
    founder_1: Optional[str] = None
    advisor_1: Optional[str] = None
    paid_1: Optional[str] = None
    board_1: Optional[str] = None
    no_coi_1: Optional[str] = None
    no_funder_role_1: Optional[str] = None
    is_fund_pred: Optional[bool] = None
    fund_text: Optional[str] = None
    fund_pmc_institute: Optional[str] = None
    fund_pmc_source: Optional[str] = None
    fund_pmc_anysource: Optional[str] = None
    is_fund_pmc_group: Optional[bool] = None
    is_fund_pmc_title: Optional[str] = None
    is_fund_pmc_anysource: Optional[str] = None
    is_relevant_fund: Optional[str] = None
    is_explicit_fund: Optional[str] = None
    support_1: Optional[str] = None
    support_3: Optional[str] = None
    support_4: Optional[str] = None
    support_5: Optional[str] = None
    support_6: Optional[str] = None
    support_7: Optional[str] = None
    support_8: Optional[str] = None
    support_9: Optional[str] = None
    support_10: Optional[str] = None
    developed_1: Optional[str] = None
    received_1: Optional[str] = None
    received_2: Optional[str] = None
    recipient_1: Optional[str] = None
    authors_1: Optional[str] = None
    authors_2: Optional[str] = None
    thank_1: Optional[str] = None
    thank_2: Optional[str] = None
    fund_1: Optional[str] = None
    fund_2: Optional[str] = None
    fund_3: Optional[str] = None
    supported_1: Optional[str] = None
    financial_1: Optional[str] = None
    financial_2: Optional[str] = None
    financial_3: Optional[str] = None
    grant_1: Optional[str] = None
    french_1: Optional[str] = None
    common_1: Optional[str] = None
    common_2: Optional[str] = None
    common_3: Optional[str] = None
    common_4: Optional[str] = None
    common_5: Optional[str] = None
    acknow_1: Optional[str] = None
    disclosure_1: Optional[str] = None
    disclosure_2: Optional[str] = None
    fund_ack: Optional[str] = None
    project_ack: Optional[str] = None
    is_register_pred: Optional[bool] = None
    register_text: Optional[str] = None
    is_research: Optional[bool] = None
    is_review: Optional[bool] = None
    is_reg_pmc_title: Optional[bool] = None
    is_relevant_reg: Optional[str] = None
    is_method: Optional[str] = None
    is_NCT: Optional[str] = None
    is_explicit_reg: Optional[str] = None
    prospero_1: Optional[str] = None
    registered_1: Optional[str] = None
    registered_2: Optional[str] = None
    registered_3: Optional[str] = None
    registered_4: Optional[str] = None
    registered_5: Optional[str] = None
    not_registered_1: Optional[str] = None
    registration_1: Optional[str] = None
    registration_2: Optional[str] = None
    registration_3: Optional[str] = None
    registration_4: Optional[str] = None
    registry_1: Optional[str] = None
    reg_title_1: Optional[str] = None
    reg_title_2: Optional[str] = None
    reg_title_3: Optional[str] = None
    reg_title_4: Optional[str] = None
    funded_ct_1: Optional[str] = None
    ct_2: Optional[str] = None
    ct_3: Optional[str] = None
    protocol_1: Optional[str] = None
    is_success: Optional[bool] = None
    is_art: Optional[str] = None
    field: Optional[str] = None
    score: Optional[int] = None
    jif: Optional[float] = None
    eigenfactor_score: Optional[float] = None
    n_cite: Optional[int] = None


# Tried to define  programmatically but both ways seemed to yield a model class without type annotated fields...

# 1
#  RtransparentMetrics = type(
#     "RtransparentMetrics",
#     (Model,),
#     {n: Optional[t] for n, t in rtransparent_metric_types.items()},
# )

# 2
# Use Field to explicitly define the fields in the model
# namespace = {
#     n: (Optional[t], Field(default=None))
#     for n, t in rtransparent_metric_types.items()
# }
# Dynamically create the Pydantic/ODMantic model
# RtransparentMetrics: Type[Model] = type(
#     "RtransparentMetrics",
#     (Model,),
#     namespace,
# )
