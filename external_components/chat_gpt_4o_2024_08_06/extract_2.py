from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.program.openai import OpenAIPydanticProgram
from pydantic import BaseModel, Field

llm = OpenAI(model="gpt-4o-2024-08-06")

# response = llm.complete(
#     "Generate a sales call transcript, use real names, talk about a product, discuss some action items"
# )


class GPT_4o_2024_08_06(BaseModel):
    """
    Model for extracting information from scientific publications. These metrics
    are a summary of the publications adherence to transparent or open
    scientific practices.
    Many unavailable identifiers (PMID, PMCID etc) can be found using pubmed: https://pubmed.ncbi.nlm.nih.gov/advanced/
    """

    year: int = Field(
        description="Best attempt at extracting the year of the publication",
    )
    journal: str = Field(description="The journal in which the paper was published")
    article_type: list[str] = Field(
        description="The type of article e.g. research article, review, erratum, meta-analysis etc.",
    )
    affiliation_country: list[str] = Field(
        description="The countries of the affiliations of the authors",
    )
    institute: list[str] = Field(
        description="The institutes of the affiliations of the authors",
    )
    doi: str = Field(description="The DOI of the paper")
    pmid: int = Field(description="The PMID of the paper")
    pmcid: str = Field(description="The PMCID of the paper")
    title: str = Field(description="The title of the paper")
    authors: list[str] = Field(description="The authors of the paper")
    publisher: str = Field(description="The publisher of the paper")
    is_open_code: bool = Field(
        description="Whether there is evidence that the code used for analysis in the paper has been shared online",
    )
    code_sharing_statement: str = Field(
        description="The statement in the paper that indicates whether the code used for analysis has been shared online",
    )
    is_open_data: bool = Field(
        description="Whether there is evidence that the data used for analysis in the paper has been shared online",
    )
    data_sharing_statement: str = Field(
        description="The statement in the paper that indicates whether the data used for analysis has been shared online",
    )
    has_coi_statement: bool = Field(
        description="Whether there is a conflict of interest statement in the paper",
    )
    coi_statement: str = Field(
        description="The conflict of interest statement in the paper"
    )
    funder: list[str] = Field(
        description="The funders of the research, may contain multiple funders",
    )
    has_funding_statement: bool = Field(
        description="Whether there is a funding statement in the paper"
    )
    funding_statement: str = Field(description="The funding statement in the paper")
    has_registration_statement: bool = Field(
        description="Whether there is a registration statement in the paper",
    )
    registration_statement: str = Field(
        description="The registration statement in the paper"
    )
    reasoning_steps: list[str] = Field(
        description="The reasoning steps used to extract the information from the paper",
    )


prompt = ChatPromptTemplate(
    message_templates=[
        ChatMessage(
            role="system",
            content=(
                "You are an expert at extracting information from scientific publications with a keen eye for details that when combined together allows you to summarize aspects of the publication"
            ),
        ),
        ChatMessage(
            role="user",
            content=(
                "Here is the transcript: \n" "------\n" "{xml_content}\n" "------"
            ),
        ),
    ]
)
program = OpenAIPydanticProgram.from_defaults(
    output_cls=GPT_4o_2024_08_06,
    llm=llm,
    prompt=prompt,
    verbose=True,
)
