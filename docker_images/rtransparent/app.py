import logging
import tempfile
from pathlib import Path

import psutil
import rpy2.robjects as ro
from fastapi import FastAPI, HTTPException, Request, status
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
    xml_content: bytes, workers: int = psutil.cpu_count()
):
    rtransparent = importr("rtransparent")
    future = importr("future")
    future.plan(future.multisession, workers=workers)

    # Write the XML content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_xml_file:
        temp_xml_file.write(xml_content)
        temp_xml_file_path = temp_xml_file.name

    with (ro.default_converter + pandas2ri.converter).context():
        df = ro.conversion.get_conversion().rpy2py(
            rtransparent.rt_all(temp_xml_file_path)
        )

    # Clean up the temporary file
    temp_xml_file.close()
    Path(temp_xml_file_path).unlink()

    return df


# from osm.schemas import Invocation
@app.post("/extract-metrics")
async def extract_metrics(request: Request):
    try:
        xml_content = await request.body()
        metrics_df = rtransparent_metric_extraction(xml_content)
        logger.critical(metrics_df)
        metrics_json = metrics_df.to_json(orient="records")
        return JSONResponse(content=metrics_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
