from fastapi import APIRouter
from services.data_service import DataService

router = APIRouter()
data_service = DataService()


@router.get("/summary")
async def get_summary():
    return data_service.get_summary()


@router.get("/timeseries")
async def get_timeseries():
    return data_service.get_timeseries()


@router.get("/country-distribution")
async def get_country_distribution():
    return data_service.get_country_distribution()


@router.get("/journal-distribution")
async def get_journal_distribution():
    return data_service.get_journal_distribution()
