import logging

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import LLM, ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.program.openai import OpenAIPydanticProgram

# from pydantic import BaseModel, Field
from osm.schemas.metrics_schemas import LLMExtractor

LLM_MODELS = {"gpt-4o-2024-08-06": OpenAI(model="gpt-4o-2024-08-06")}


logger = logging.getLogger(__name__)
app = FastAPI()


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


def llm_metric_extraction(
    xml_content: bytes,
    llm_model: str,
):
    return extract_with_llm(xml_content, LLM_MODELS[llm_model])


@app.post("/extract-metrics/", response_model=LLMExtractor)
async def extract_metrics(
    file: UploadFile = File(...), llm_model: str = Query("other")
):
    try:
        xml_content = await file.read()
        if not xml_content:
            raise NotImplementedError(
                """For now the XML content must be provided. Check the output of
                the parsing stage."""
            )
        metrics = llm_metric_extraction(xml_content, llm_model)
        logger.info(metrics)
        return metrics

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
