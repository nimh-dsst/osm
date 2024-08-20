import os

import holoviews as hv
import pandas as pd
import panel as pn
from odmantic import SyncEngine
from pymongo import MongoClient

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


def get_dashboard():
    data_grouped = pn.state.cache["data_grouped"]

    # Create charts
    fig_data = hv.Bars(
        data_grouped,
        kdims=["year"],
        vdims=[
            "percent_is_data_pred",
        ],
    )
    fig_code = hv.Bars(
        data_grouped,
        kdims=["year"],
        vdims=[
            "percent_is_code_pred",
        ],
    )
    # Layout the dashboard
    dashboard = pn.Column(
        "# Data and code transparency",
        pn.Row(fig_data, fig_code, sizing_mode="stretch_width"),
    )
    return dashboard


def on_load():
    """
    Add resource intensive things that you only want to run once.
    """
    pn.config.browser_info = True
    pn.config.notifications = True
    pn.state.cache["data"] = load_data()
    pn.state.cache["data_grouped"] = (
        pn.state.cache["data"][pn.state.cache["data"]["year"] != 999999]
        .groupby("year")
        .agg(
            percent_is_data_pred=("is_data_pred", lambda x: x.mean() * 100),
            percent_is_code_pred=("is_code_pred", lambda x: x.mean() * 100),
            avg_score=("score", "mean"),
            avg_eigenfactor_score=("eigenfactor_score", "mean"),
        )
        .reset_index()
    )


if __name__ == "__main__":
    # Runs all the things necessary before the server actually starts.
    pn.state.onload(on_load)
    print("starting dashboard!")
    pn.serve(
        get_dashboard(),
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
