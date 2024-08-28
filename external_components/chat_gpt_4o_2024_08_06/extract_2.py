from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import LLM, ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.program.openai import OpenAIPydanticProgram
from pydantic import BaseModel, Field

llm = OpenAI(model="gpt-4o-2024-08-06")


class LLMExtractor(BaseModel):
    """
    Model for extracting information from scientific publications. These metrics
    are a summary of the publications adherence to transparent or open
    scientific practices.
    Many unavailable identifiers (PMID, PMCID etc) can be found using pubmed: https://pubmed.ncbi.nlm.nih.gov/advanced/
    """

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
    affiliation_country: list[str] = Field(
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


def get_program(llm: LLM) -> OpenAIPydanticProgram:
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
                    "The llm model is {llm_model}. The publication in xml follows below:\n"
                    "------\n"
                    "{xml_content}\n"
                    "------"
                ),
            ),
        ]
    )

    program = OpenAIPydanticProgram.from_defaults(
        output_cls=LLMExtractor,
        llm=llm,
        prompt=prompt,
        verbose=True,
    )
    return program


def extract_with_llm(xml_content: bytes, llm: LLM) -> LLMExtractor:
    program = get_program(llm=llm)
    return program(xml_content=xml_content, llm_model=llm.model)
