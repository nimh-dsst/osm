import os
from typing import Dict, List

import pandas as pd

DATA_PATH = os.getenv("DATA_PATH", "/opt/data/matches.parquet")


class DataService:
    def __init__(self):
        self.df = pd.read_parquet(DATA_PATH)

    def get_summary(self) -> Dict:
        return {
            "totalRecords": len(self.df),
            "openCodePercentage": float(self.df["is_open_code"].mean() * 100),
            "openDataPercentage": float(self.df["is_open_data"].mean() * 100),
            "uniqueJournals": int(self.df["journal"].nunique()),
            "uniqueCountries": int(self.df["affiliation_country"].nunique()),
        }

    def get_timeseries(self) -> List[Dict]:
        yearly_stats = (
            self.df.groupby("year")
            .agg({"is_open_code": "mean", "is_open_data": "mean"})
            .reset_index()
        )

        return [
            {
                "year": int(row["year"]),
                "openCode": round(float(row["is_open_code"] * 100), 2),
                "openData": round(float(row["is_open_data"] * 100), 2),
            }
            for _, row in yearly_stats.iterrows()
        ]

    def get_country_distribution(self) -> List[Dict]:
        return self.df["affiliation_country"].value_counts().head(10).to_dict()

    def get_journal_distribution(self) -> List[Dict]:
        return self.df["journal"].value_counts().head(10).to_dict()
