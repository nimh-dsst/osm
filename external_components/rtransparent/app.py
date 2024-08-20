import logging
import tempfile
from pathlib import Path

import pandas as pd
import psutil
import rpy2.robjects as ro
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

ro.r(f'Sys.setenv(VROOM_CONNECTION_SIZE = "{2**20}")')

logger = logging.getLogger(__name__)
app = FastAPI()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


def rtransparent_metric_extraction(
    xml_content: bytes, parser: str, workers: int = psutil.cpu_count()
):
    rtransparent = importr("rtransparent")
    future = importr("future")
    future.plan(future.multisession, workers=workers)

    # Write the XML content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_xml_file:
        temp_xml_file.write(xml_content)
        temp_xml_file_path = temp_xml_file.name
    if parser == "pmc":
        df = extract_from_pmc_xml(temp_xml_file_path, rtransparent)
    else:
        df = extract_from_xml(temp_xml_file_path, rtransparent)
    # Clean up the temporary file
    temp_xml_file.close()
    Path(temp_xml_file_path).unlink()
    return df


def extract_from_xml(temp_xml_file_path, rtransparent):
    dfs = {}
    with (ro.default_converter + pandas2ri.converter).context():
        dfs["data_code"] = ro.conversion.get_conversion().rpy2py(
            rtransparent.rt_data_code(temp_xml_file_path)
        )
    #  "all" contains fund, register, and coi outputs
    with (ro.default_converter + pandas2ri.converter).context():
        dfs["all"] = ro.conversion.get_conversion().rpy2py(
            rtransparent.rt_all(temp_xml_file_path)
        )
    return pd.concat([dfs["all"], dfs["data_code"].drop(columns=["article"])], axis=1)


def extract_from_pmc_xml(temp_xml_file_path, rtransparent):
    raise NotImplementedError(
        "Not all XML files provided at pubmedcentral include the datasharing statements."
    )
    # dfs = {}
    # with (ro.default_converter + pandas2ri.converter).context():
    #     dfs["meta_pmc"] = ro.conversion.get_conversion().rpy2py(
    #         rtransparent.rt_meta_pmc(temp_xml_file_path)
    #     )
    # # data_code_pmc is a subset of all_pmc
    # with (ro.default_converter + pandas2ri.converter).context():
    #     dfs["all_pmc"] = ro.conversion.get_conversion().rpy2py(
    #         rtransparent.rt_all_pmc(temp_xml_file_path)
    #     )
    # return pd.concat(
    #     [
    #         dfs["all_pmc"],
    #         dfs["meta_pmc"].drop(
    #             columns=["doi", "filename", "is_success", "pmcid_pmc", "pmid"]
    #         ),
    #     ],
    #     axis=1,
    # )


@app.post("/extract-metrics/")
async def extract_metrics(request: Request, parser: str = Query("other")):
    try:
        # Attempt to read the XML content from the request body
        xml_content = await request.body()
        if not xml_content:
            raise NotImplementedError(
                """For now the XML content must be provided. Check the output of
                the parsing stage."""
            )

        metrics_df = rtransparent_metric_extraction(xml_content, parser)

        # Log the extracted metrics
        logger.info(metrics_df)

        # Return the first row as a JSON response
        return JSONResponse(content=metrics_df.iloc[0].to_dict(), status_code=200)

    except Exception as e:
        # Handle exceptions and return a 500 Internal Server Error
        raise HTTPException(status_code=500, detail=str(e))
