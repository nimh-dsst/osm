import os

import pandas as pd
import panel as pn
from main_dashboard import MainDashboard
from odmantic import SyncEngine
from pymongo import MongoClient
from ui import get_template

from osm import schemas


def flatten_dict(d):
    """
    Recursively flattens a nested dictionary without prepending parent keys.

    :param d: Dictionary to flatten.
    :return: Flattened dictionary.
    """
    items = []
    for k, v in d.items():
        if isinstance(v, dict):
            # If the value is a dictionary, flatten it without the parent key
            items.extend(flatten_dict(v).items())
        else:
            items.append((k, v))
    return dict(items)


def load_data():
    if "LOCAL_DATA_PATH" in os.environ:
        return pd.read_feather(os.environ["LOCAL_DATA_PATH"])
    client = MongoClient(os.environ["MONGODB_URI"])
    engine = SyncEngine(client=client, database="osm")
    matches = (
        engine.get_collection(schemas.Invocation)
        .aggregate(
            [
                {
                    "$match": {
                        "osm_version": {"$eq": "0.0.1"},
                        # "work.pmid": {"$regex":r"^2"},
                        "metrics.year": {"$gt": 2000},
                        # "metrics.is_data_pred": {"$eq": True},
                    },
                },
                {
                    "$project": {
                        # "osm_version": True,
                        # "user_comment": True,
                        # "client.compute_context_id": True,
                        "work.user_defined_id": True,
                        "metrics.year": True,
                        "metrics.is_code_pred": True,
                        "metrics.is_data_pred": True,
                        "metrics.affiliation_country": True,
                        "metrics.score": True,
                        "metrics.eigenfactor_score": True,
                        "metrics.fund_pmc_anysource": True,
                        "metrics.fund_pmc_institute": True,
                        "metrics.fund_pmc_source": True,
                        "metrics.journal": True,
                    },
                },
            ]
        )
        .__iter__()
    )
    return pd.DataFrame(flatten_dict(match) for match in matches)


def dashboard_page():
    template = get_template()

    dashboard = MainDashboard({"RTransparent": pn.state.cache["data"]})

    template.main.append(dashboard.get_dashboard)
    template.sidebar.append(dashboard.get_sidebar)

    return template


def on_load():
    """
    Add resource intensive things that you only want to run once.
    """
    pn.config.browser_info = True
    pn.config.notifications = True
    raw_data = load_data()
    raw_data = raw_data[raw_data != 999999]

    # Harcoded for now, will be added to the raw data later
    raw_data["metrics"] = "RTransparent"

    pn.state.cache["data"] = raw_data


if __name__ == "__main__":
    # Runs all the things necessary before the server actually starts.
    pn.state.onload(on_load)
    print("starting dashboard!")
    pn.serve(
        {"/": dashboard_page},
        address="0.0.0.0",
        port=8501,
        start=True,
        location=True,
        show=False,
        keep_alive=30 * 1000,  # 30s
        autoreload=True,
        admin=True,
        profiler="pyinstrument",
        allow_websocket_origin=[
            "localhost:8501",
            "osm.pythonaisolutions.com",
        ],
    )
