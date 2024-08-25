import os
from pathlib import Path

import pandas as pd
import panel as pn
import param
import ui
from main_dashboard import MainDashboard
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


class OSMApp(param.Parameterized):
    def __init__(self):
        super().__init__()

        # Apply the design modifiers to the panel components
        # It returns all the CSS files of the modifiers
        self.css_filepaths = ui.apply_design_modifiers()

    def get_template(self):
        # A bit hacky, but works.
        # we need to preload the css files to avoid a flash of unstyled content, especially when switching between chats.
        # This is achieved by adding <link ref="preload" ...> tags in the head of the document.
        # But none of the panel templates allow to add custom link tags in the head.
        # the only way I found is to take advantage of the raw_css parameter, which allows to add custom css in the head.
        preload_css = "\n".join(
            [
                f"""<link rel="preload" href="{css_fp}" as="style" />"""
                for css_fp in self.css_filepaths
            ]
        )
        preload_css = f"""
                     </style>
                     {preload_css}
                     <style type="text/css">
                     """

        template = pn.template.FastListTemplate(
            site="NIH",
            title="OpenSciMetrics",
            favicon="https://www.nih.gov/favicon.ico",
            sidebar=[],
            accent=ui.MAIN_COLOR,
            theme_toggle=False,
            raw_css=[ui.CSS_VARS, ui.CSS_GLOBAL, preload_css],
            css_files=[
                "https://rsms.me/inter/inter.css",
                "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",
                "css/global/intro.css",
            ],
        )
        # <link rel="preconnect" href="https://fonts.googleapis.com">
        # <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        # <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
        template.header.append(
            ui.connection_monitor(),
        )

        return template

    def dashboard_page(self):
        template = self.get_template()
        dashboard = MainDashboard({"RTransparent": pn.state.cache["data"]})
        template.main.append(dashboard.get_dashboard())
        template.sidebar.append(dashboard.get_sidebar())

        return template

    def serve(self):
        pn.serve(
            {"/": self.dashboard_page},
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
            static_dirs={
                dir: str(Path(__file__).parent / dir)
                for dir in ["css"]  # add more directories if needed
            },
        )


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

    # Cleanup - might be handlded upstream in the future
    # raw_countries = raw_data.affiliation_country.unique()

    raw_data.affiliation_country = raw_data.affiliation_country.apply(
        lambda cntry: (
            tuple(set(map(str.strip, cntry.split(";")))) if cntry is not None else cntry
        )
    )

    pn.state.cache["data"] = raw_data


if __name__ == "__main__":
    # Runs all the things necessary before the server actually starts.
    pn.state.onload(on_load)
    print("starting dashboard!")

    OSMApp().serve()
