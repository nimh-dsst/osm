from typing import Optional

from odmantic import EmbeddedModel, Field
from openai import OpenAI

client = OpenAI()


class GPT_4o_2024_08_06(EmbeddedModel):
    year: Optional[int] = Field(
        description="Best attempt at extracting the year of the publication",
    )
    journal: Optional[str] = Field(
        description="The journal in which the paper was published"
    )
    article_type: list[str] = Field(
        description="The type of article e.g. research article, review, erratum, meta-analysis etc.",
    )
    affiliation_country: list[str] = Field(
        description="The countries of the affiliations of the authors",
    )
    institute: list[str] = Field(
        description="The institutes of the affiliations of the authors",
    )
    doi: Optional[str] = Field(description="The DOI of the paper")
    pmid: Optional[int] = Field(description="The PMID of the paper")
    pmcid: Optional[str] = Field(description="The PMCID of the paper")
    title: Optional[str] = Field(description="The title of the paper")
    authors: list[str] = Field(description="The authors of the paper")
    publisher: Optional[str] = Field(description="The publisher of the paper")
    is_open_code: Optional[bool] = Field(
        description="Whether there is evidence that the code used for analysis in the paper has been shared online",
    )
    code_sharing_statement: Optional[str] = Field(
        description="The statement in the paper that indicates whether the code used for analysis has been shared online",
    )
    is_open_data: Optional[bool] = Field(
        description="Whether there is evidence that the data used for analysis in the paper has been shared online",
    )
    data_sharing_statement: Optional[str] = Field(
        description="The statement in the paper that indicates whether the data used for analysis has been shared online",
    )
    has_coi_statement: Optional[bool] = Field(
        description="Whether there is a conflict of interest statement in the paper",
    )
    coi_statement: Optional[str] = Field(
        description="The conflict of interest statement in the paper"
    )
    funder: list[str] = Field(
        description="The funders of the research, may contain multiple funders",
    )
    has_funding_statement: Optional[bool] = Field(
        description="Whether there is a funding statement in the paper"
    )
    funding_statement: Optional[str] = Field(
        description="The funding statement in the paper"
    )
    has_registration_statement: Optional[bool] = Field(
        description="Whether there is a registration statement in the paper",
    )
    registration_statement: Optional[str] = Field(
        description="The registration statement in the paper"
    )
    reasoning_steps: list[str] = Field(
        description="The reasoning steps used to extract the information from the paper",
    )


def parse_xml_content(xml_content: bytes) -> GPT_4o_2024_08_06:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. The current date is August 6, 2024. You help users search through a publication (an XML text is provided) and search online to populate their metrics of transparent science.",
            },
            {
                "role": "user",
                "content": f'{xml_content.decode("utf-8")[:100]}',
            },
        ],
        response_format=GPT_4o_2024_08_06.__pydantic_model__,
    )
    return completion.messages[-1].content
