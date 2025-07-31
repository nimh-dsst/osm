import json
from datetime import datetime
from functools import lru_cache

import colorcet as cc
import pandas as pd
import panel as pn
import param
from components.select_picker import SelectPicker
from ui import MAIN_COLOR, divider

pn.extension(
    "echarts",
    "codeeditor",
)

pd.options.display.max_columns = None


groups = {"year": "int"}

extraction_tools_params = {
    "RTransparent": {
        "metrics": [
            "is_open_data",
            "is_open_code",
        ],
        "splitting_vars": [
            "None",
            "journal",
            "affiliation_country",
            "funder",
            "data_tags",
        ],
        "labels": {
            "None": "None",
            "journal": "Journal",
            "affiliation_country": "Country",
            "funder": "Funder",
            "data_tags": "Tags",
        },
    }
}

dims_aggregations = {
    "is_open_data": ["percent", "count_true", "count"],
    "is_open_code": [
        "percent",
        "count_true",
    ],
    # "score": ["mean"],
    # "eigenfactor_score": ["mean"],
}

metrics_titles = {
    "percent_is_open_data": "Data Sharing (%)",
    "percent_is_open_code": "Code Sharing (%)",
    "count_true_is_open_data": "Data Sharing",
    "count_true_is_open_code": "Code Sharing",
    "count_is_open_data": "Total number of publications",
    "mean_score": "Mean Score",
    "mean_eigenfactor_score": "Mean Eigenfactor Score",
}

metrics_by_title = {v: k for k, v in metrics_titles.items()}


aggregation_formulas = {
    "percent": "mean",
    "count_true": "sum",
    "count": "count",
    "mean": "mean",
}


class MainDashboard(param.Parameterized):
    """
    Main dashboard for the application.
    """

    # High-level parameters.
    extraction_tool = param.Selector(default="", objects=[], label="Metrics group")

    metrics = param.Selector(default=[], objects=[], label="Metrics")

    splitting_var = param.Selector(
        objects=[],
        label="Splitting Variable",
    )

    # Filters
    filter_pubdate = param.Range(step=1, label="Publication date")

    filter_journal = param.ListSelector(default=[], objects=[], label="Journal")

    filter_affiliation_country = param.ListSelector(
        default=[], objects=[], label="Country"
    )

    filter_funder = param.ListSelector(default=[], objects=[], label="Funder")

    filter_tags = param.ListSelector(default=[], objects=[], label="Tags")

    # Internal mechanisms
    trigger_rendering = param.Integer(default=0)

    # UI elements
    echarts_pane = pn.pane.ECharts(
        {}, height=640, width=1200, renderer="svg", options={"replaceMerge": ["series"]}
    )

    # set up in the init method
    journal_select_picker = None
    affiliation_country_select_picker = None
    funder_select_picker = None
    tags_select_picker = None

    # DEBUG
    # This is a code editor to update the ECharts config and render the plot from the browser
    # without having to restart the server.

    # Switch this to True to enable it.
    debug = False

    echarts_config_editor = pn.widgets.CodeEditor(
        value="", sizing_mode="stretch_width", language="javascript", height=800
    )
    echarts_update_button = pn.widgets.Button(name="Update ECharts")
    echarts_config = param.Dict(default={})

    def __init__(self, datasets, **params):
        super().__init__(**params)

        self.datasets = datasets

        # By default, take the first dataset.
        # Currently, there's only RTransparent
        self.param.extraction_tool.objects = [
            *list(self.datasets.keys()),
            *["Manual curation", "GPT_4o_2024_08_06"],
        ]
        self.extraction_tool = self.param.extraction_tool.objects[0]

        self.journal_select_picker = SelectPicker.from_param(
            self.param.filter_journal,
            annotations={
                row[0]: row[1]
                for row in self.raw_data.journal.value_counts().reset_index().values
            },
            update_title_callback=lambda select_picker,
            values,
            options: self.new_picker_title("journals", select_picker, values, options),
        )

        self.affiliation_country_select_picker = SelectPicker.from_param(
            self.param.filter_affiliation_country,
            annotations=self.get_col_values_with_count("affiliation_country"),
            update_title_callback=lambda select_picker,
            values,
            options: self.new_picker_title(
                "affiliation countries", select_picker, values, options
            ),
        )

        self.funder_select_picker = SelectPicker.from_param(
            self.param.filter_funder,
            annotations=self.get_col_values_with_count("funder"),
            update_title_callback=lambda select_picker,
            values,
            options: self.new_picker_title("funders", select_picker, values, options),
        )

        self.tags_select_picker = SelectPicker.from_param(
            self.param.filter_tags,
            annotations=self.get_col_values_with_count("data_tags"),
            update_title_callback=lambda select_picker,
            values,
            options: self.new_picker_title("tags", select_picker, values, options),
        )

        self.build_pubdate_filter()

        # DEBUG
        self.echarts_update_button.on_click(self.did_click_update_echart_plot)

    def splitting_var_label(self, splitting_var):
        return extraction_tools_params[self.extraction_tool]["labels"][splitting_var]

    def splitting_var_from_label(self, label):
        return [
            k
            for k, v in extraction_tools_params[self.extraction_tool]["labels"].items()
            if v == label
        ][0]

    @pn.depends("extraction_tool", watch=True)
    def did_change_extraction_tool(self):
        print("DID_CHANGE_EXTRACTION_TOOL")

        # Update the raw data
        self.raw_data = self.datasets[self.extraction_tool]

        # Updated the metrics param
        new_extraction_tools_metrics = extraction_tools_params[self.extraction_tool][
            "metrics"
        ]

        new_metrics = []
        for m in new_extraction_tools_metrics:
            for agg in dims_aggregations[m]:
                new_metrics.append(metrics_titles[f"{agg}_{m}"])

        self.param.metrics.objects = new_metrics
        self.metrics = self.param.metrics.objects[0]

        # Update the splitting_var param
        new_extraction_tools_splitting_vars = extraction_tools_params[
            self.extraction_tool
        ]["splitting_vars"]
        self.param.splitting_var.objects = [
            self.splitting_var_label(v) for v in new_extraction_tools_splitting_vars
        ]

        # Update the filters
        ## filter_pubdate
        self.param.filter_pubdate.bounds = (
            self.raw_data.year.min(),
            # self.raw_data.year.max(),
            # Use current year instead, so the "Past X years" buttons work
            datetime.now().year,
        )
        self.param.filter_pubdate.default = (
            self.raw_data.year.min(),
            self.raw_data.year.max(),
        )
        self.filter_pubdate = (self.raw_data.year.min(), self.raw_data.year.max())

        ## filter_journal

        self.param.filter_journal.objects = (
            self.raw_data.journal.value_counts().index.to_list()
        )
        # If we don't want to sort the journals by number of paper,
        # but by alphabetical order, we can use this instead:
        # self.param.filter_journal.objects = self.raw_data.journal.unique()

        ## affiliation country
        countries_with_count = self.get_col_values_with_count("affiliation_country")

        def country_sorter(c):
            return countries_with_count[c]

        self.param.filter_affiliation_country.objects = sorted(
            countries_with_count.keys(), key=country_sorter, reverse=True
        )

        ## funder
        funders_with_count = self.get_col_values_with_count("funder")

        def funder_sorter(c):
            return funders_with_count[c]

        self.param.filter_funder.objects = sorted(
            funders_with_count.keys(), key=funder_sorter, reverse=True
        )

        ## Tags
        tags_with_count = self.get_col_values_with_count("data_tags")

        def tags_sorter(c):
            return tags_with_count[c]

        self.param.filter_tags.objects = sorted(
            tags_with_count.keys(), key=tags_sorter, reverse=True
        )

        # This triggers function "did_change_splitting_var"
        # which updates filter_journal, filter_affiliation_country and filter_funder
        self.splitting_var = self.param.splitting_var.objects[0]

    @lru_cache
    def get_col_values_with_count(self, col, none_test=lambda row: "None" in row):
        values = {}
        for row in self.raw_data[col].values:
            if none_test(row):
                ## Keeping "None" as a string on purpose, to represent it in the SelectPicker
                values["None"] = values.get("None", 0) + 1
            else:
                for c in row:
                    values[c] = values.get(c, 0) + 1
        return values

    @pn.depends("splitting_var", watch=True)
    def did_change_splitting_var(self):
        print("DID_CHANGE_SPLITTING_VAR", self.splitting_var)

        # already set the echarts pane as loading for a better UX
        self.echarts_pane.loading = True

        splitting_var = self.splitting_var_from_label(self.splitting_var)

        notif_msg = None
        if splitting_var == "journal":
            # We want to show all journals, but pre-select only the top 10
            selected_journals = list(
                self.raw_data.query("journal != 'None'")
                .journal.value_counts()
                .iloc[:10]
                .index
            )
            notif_msg = "Splitting by journal. Top 10 journals selected by default."
        else:
            selected_journals = self.param.filter_journal.objects

        if splitting_var == "affiliation_country":
            # We want to show all countries, but pre-select only the top 10
            countries_with_count = self.get_col_values_with_count("affiliation_country")

            # pre-filter the countries because there are a lot
            countries_with_count = {
                country: count
                for country, count in countries_with_count.items()
                if count > 10
            }

            top_10_min = sorted(
                [
                    count
                    for country, count in countries_with_count.items()
                    if country != "None"
                ],
                reverse=True,
            )[10]
            selected_countries = [
                country
                for country, count in countries_with_count.items()
                if count > top_10_min and country != "None"
            ]

            notif_msg = "Splitting by affiliation country. Top 10 countries selected by default."
        else:
            selected_countries = self.param.filter_affiliation_country.objects

        if splitting_var == "funder":
            # We want to show all funders, but pre-select only the top 10
            funders_with_count = self.get_col_values_with_count("funder")

            top_5_min = sorted(
                [
                    count
                    for funder, count in funders_with_count.items()
                    if funder != "None"
                ],
                reverse=True,
            )[5]
            selected_funders = [
                funder
                for funder, count in funders_with_count.items()
                if count > top_5_min and funder != "None"
            ]

            notif_msg = "Splitting by funder. Top 5 Funders selected by default."
        else:
            selected_funders = self.param.filter_funder.objects

        # There is currently only two tags, so no need to pre-select a top subset
        selected_tags = self.param.filter_tags.objects

        # Trigger a batch update of the filters value,
        # preventing from re-rendering the dashboard several times
        # and preventing intermediate states where the dashboard renders onces
        # with all funders for instance, and then restricting on the selected funders.
        # Also, we increment the trigger_rendering to force the update of the echarts plot.
        # This is usefull when switching from splitting var "None" to "data_tags" for instance.
        # In this case, the selected tags don't change, and the plot won't update, hence the need
        # for trigger_rendering.
        print("TRIGGER UPDATE")
        self.param.update(
            filter_journal=selected_journals,
            filter_affiliation_country=selected_countries,
            filter_funder=selected_funders,
            filter_tags=selected_tags,
            trigger_rendering=self.trigger_rendering + 1,
        )

        # Hack to force re-rendering the select pickers
        if self.affiliation_country_select_picker is not None:
            self.journal_select_picker.trigger_rendering += 1
            self.affiliation_country_select_picker.trigger_rendering += 1
            self.funder_select_picker.trigger_rendering += 1
            self.tags_select_picker.trigger_rendering += 1

        if splitting_var == "None":
            notif_msg = "No more splitting. Filters reset to default"

        if notif_msg is not None:
            pn.state.notifications.info(notif_msg, duration=5000)

    def filtered_grouped_data(self):
        print("FILTERED_GROUPED_DATA")

        filters = []

        if len(self.filter_journal) != self.param.filter_journal.objects:
            filters.append(f"journal in {self.filter_journal}")

        if self.filter_pubdate is not None:
            filters.append(f"year >= {self.filter_pubdate[0]}")
            filters.append(f"year <= {self.filter_pubdate[1]}")

        filtered_df = (
            self.raw_data.query(" and ".join(filters)) if filters else self.raw_data
        )

        if len(self.filter_affiliation_country) != len(
            self.param.filter_affiliation_country.objects
        ):
            # the filter on countries is a bit different as the rows
            # are list of countries
            def country_filter(cell):
                if len(cell) == 0 or len(cell) == 1 and cell[0] == "":
                    return "None" in self.filter_affiliation_country
                return any(c in self.filter_affiliation_country for c in cell)

            filtered_df = filtered_df[
                filtered_df.affiliation_country.apply(country_filter)
            ]
            print("FILTERED_GROUPED_DATA_COUNTRY", len(filtered_df))

        if len(filtered_df) > 0 and len(self.filter_funder) != len(
            self.param.filter_funder.objects
        ):
            # the filter on funders is similar to the filter on countries
            def funder_filter(cell):
                if len(cell) == 0 or len(cell) == 1 and cell[0] == "":
                    return "None" in self.filter_funder
                return any(c in self.filter_funder for c in cell)

            filtered_df = filtered_df[filtered_df.funder.apply(funder_filter)]

        if len(filtered_df) > 0 and len(self.filter_tags) != len(
            self.param.filter_tags.objects
        ):
            # the filter on tags is similar to the filter on countries
            def tags_filter(cell):
                if len(cell) == 0 or len(cell) == 1 and cell[0] == "":
                    return "None" in self.filter_tags
                return any(c in self.filter_tags for c in cell)

            filtered_df = filtered_df[filtered_df.data_tags.apply(tags_filter)]

        aggregations = {}
        for field, aggs in dims_aggregations.items():
            for agg in aggs:
                aggregations[f"{agg}_{field}"] = (field, aggregation_formulas[agg])

        groupers = ["year"]
        if self.splitting_var != "None":
            groupers.append(self.splitting_var_from_label(self.splitting_var))

        result = filtered_df.groupby(groupers).agg(**aggregations).reset_index()

        for col in aggregations:
            if col.startswith("percent_"):
                result[col] = result[col] * 100

        print("FILTERED_GROUPED_DATA_DONE", len(result))

        return result

    @pn.depends(
        "metrics",
        "filter_pubdate",
        "filter_affiliation_country",
        "filter_journal",
        "filter_funder",
        "filter_tags",
        "trigger_rendering",
        watch=True,
    )
    def updated_echart_plot(self):
        print("ECHART_PLOT")

        if self.filter_pubdate is None:
            # The filters are not yet initialized
            # Let's return an empty plot
            return self.echarts_pane

        self.echarts_pane.loading = True

        df = self.filtered_grouped_data()

        raw_metric = metrics_by_title[self.metrics]

        xAxis = df["year"].unique().tolist()

        if self.splitting_var == "None":
            title = f"{self.metrics} ({int(self.filter_pubdate[0])}-{int(self.filter_pubdate[1])})"
            series = [
                {
                    "id": self.metrics,
                    "name": self.metrics,
                    "type": "line",
                    "data": df[raw_metric].tolist(),
                }
            ]
            legend_data = [
                {"name": self.metrics, "icon": "path://M 0 0 H 20 V 20 H 0 Z"},
            ]
            colormap = [MAIN_COLOR]
        else:
            title = f"{self.metrics} by {self.splitting_var} ({int(self.filter_pubdate[0])}-{int(self.filter_pubdate[1])})"

            series = []
            legend_data = []

            splitting_var = self.splitting_var_from_label(self.splitting_var)

            if splitting_var == "affiliation_country":
                splitting_var_filter = self.filter_affiliation_country
                splitting_var_column = "affiliation_country"
                splitting_var_query = lambda cell, selected_item: selected_item in cell  # noqa: E731

            elif splitting_var == "funder":
                splitting_var_filter = self.filter_funder
                splitting_var_column = "funder"
                splitting_var_query = lambda cell, selected_item: selected_item in cell  # noqa: E731

            elif splitting_var == "data_tags":
                splitting_var_filter = self.filter_tags
                splitting_var_column = "data_tags"
                splitting_var_query = lambda cell, selected_item: selected_item in cell  # noqa: E731

            else:
                print("Defaulting to splitting var 'journal' ")
                splitting_var_filter = self.filter_journal
                splitting_var_column = "journal"
                splitting_var_query = lambda cell, selected_item: cell == selected_item  # noqa: E731

            last_year_values = {}
            for selected_item in sorted(splitting_var_filter):
                # sub_df = df.query(f"{splitting_var_column} == '{selected_item}'")

                sub_df = df[
                    df[splitting_var_column].apply(
                        lambda x: splitting_var_query(x, selected_item)
                    )
                ]

                if len(sub_df) > 0:
                    aggregation = "mean" if "percent" in raw_metric else "sum"
                    sub_df = (
                        sub_df.groupby("year")
                        .agg({raw_metric: aggregation})
                        .reset_index()
                    )

                    value_last_year = sub_df[sub_df.year == sub_df.year.max()][
                        raw_metric
                    ].values[0]
                    last_year_values[selected_item] = value_last_year

                    data_as_dict = sub_df.set_index("year")[raw_metric].to_dict()
                    data = [data_as_dict.get(year, None) for year in xAxis]

                    series.append(
                        {
                            "id": selected_item,
                            "name": selected_item,
                            "type": "line",
                            "data": data,
                            # Shows a label at the end of the plotted line.
                            # Labels end up overlapping in some cases.
                            # To fix this, we would need to change the offset of the label
                            # with values calculated to avoid overlapping.
                            # https://echarts.apache.org/en/option.html#series-line.endLabel.offset
                            # "endLabel":{
                            #     "formatter":selected_item,
                            #     "show":True,
                            # }
                        }
                    )
                    legend_data.append(
                        {"name": selected_item, "icon": "path://M 0 0 H 20 V 20 H 0 Z"}
                    )

            # Sort the legend series by decreasing order of the last year value
            legend_data.sort(
                key=lambda x: last_year_values.get(x["name"], 0), reverse=True
            )

            colormap = cc.glasbey_light

        # Hack for the tooltip.
        # The tooltip shows values with 15 decimals, which is not very useful.
        # We could use the formatter option of the tooltip, but it requires a bit of
        # time to get the same good-looking result.
        # So for the sake of delivering fast, I just round the values to 2 decimals.
        for serie in series:
            serie["data"] = [round(v, 2) if v is not None else v for v in serie["data"]]

        # Default colormap is :
        # ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc"]
        # https://echarts.apache.org/en/option.html#color

        echarts_config = {
            "color": colormap,
            "title": {
                "text": title,
            },
            "grid": {
                "width": "800",
            },
            "tooltip": {
                "show": True,
                "trigger": "axis",
                "order": "valueDesc",
                # "formatter": f"""<b>{self.splitting_var}</b> : {{b0}} <br />
                #                 {{a0}} : {{c0}} <br />
                #                 {{a1}} : {{c1}} """,
            },
            "legend": {
                "data": legend_data,
                "type": "scroll",
                "orient": "vertical",
                "show": True,
                "right": "0",
                "textStyle": {"width": "250", "overflow": "break"},
            },
            "xAxis": {
                "data": xAxis,
                "name": "year",
                "nameLocation": "center",
                "nameGap": 40,
                "nameTextStyle": {
                    "fontWeight": "bold",
                    "fontFamily": "Roboto",
                    "fontSize": "20",
                },
            },
            "yAxis": {
                "name": self.metrics,
                "nameLocation": "center",
                "nameGap": 80,
                "nameTextStyle": {
                    "fontWeight": "bold",
                    "fontFamily": "Roboto",
                    "fontSize": "20",
                },
                "axisLabel": {
                    "formatter": "{value}%" if "percent" in raw_metric else "{value}"
                },
            },
            "series": series,
        }

        self.echarts_config = echarts_config
        self.echarts_config_editor.value = json.dumps(
            self.echarts_config, indent=4, sort_keys=True
        )

    @pn.depends("echarts_config", watch=True)
    def echarts_config_updated(self):
        self.echarts_pane.object = self.echarts_config
        self.echarts_pane.loading = False

    def did_click_update_echart_plot(self, event):
        print("DID_CLICK_UPDATE_ECHART_PLOT")
        self.echarts_pane.loading = True
        self.echarts_config = json.loads(self.echarts_config_editor.value)
        self.echarts_pane.object = self.echarts_config
        self.echarts_pane.loading = False

    # Below are all the functions returning the different parts of the dashboard :
    # Sidebar, Top Bar and the plot area (in function get_dashboard)

    def build_pubdate_filter(self):
        print("BUILD_PUBDATE_FILTER")

        # The text input only reflect the values of the slider bounds,
        # and update the slider bounds when their text value is changed.
        self.pubdate_slider = pn.widgets.IntRangeSlider(
            start=int(self.param.filter_pubdate.bounds[0]),
            end=int(self.param.filter_pubdate.bounds[1]),
            step=1,
        )

        # It's the textInputs that controls the filter_pubdate param
        self.start_pubdate_input = pn.widgets.TextInput(
            value=str(int(self.param.filter_pubdate.bounds[0])),
            name="From",
            css_classes=["filters-text-input", "pubdate-input"],
        )
        self.end_pubdate_input = pn.widgets.TextInput(
            value=str(int(self.param.filter_pubdate.bounds[1])),
            name="To",
            css_classes=["filters-text-input", "pubdate-input"],
        )

        # When the slider's value change, update the TextInputs
        def update_pubdate_text_inputs(event):
            self.start_pubdate_input.value = str(self.pubdate_slider.value[0])
            self.end_pubdate_input.value = str(self.pubdate_slider.value[1])

        self.pubdate_slider.param.watch(update_pubdate_text_inputs, "value_throttled")

        # When the TextInputs' value change, update the slider,
        # and update filter_pubdate
        def update_pubdate_slider(event):
            self.pubdate_slider.value = (
                int(self.start_pubdate_input.value),
                int(self.end_pubdate_input.value),
            )
            self.filter_pubdate = self.pubdate_slider.value

        self.start_pubdate_input.param.watch(update_pubdate_slider, "value")
        self.end_pubdate_input.param.watch(update_pubdate_slider, "value")

        self.last_year_button = pn.widgets.Button(
            name="Last year", width=80, css_classes=["last-year-button", "year-button"]
        )
        self.past_5years_button = pn.widgets.Button(
            name="Past 5 years",
            width=80,
            css_classes=["past-5years-button", "year-button"],
        )
        self.past_10years_button = pn.widgets.Button(
            name="Past 10 years",
            width=80,
            css_classes=["past-10years-button", "year-button"],
        )

        def did_click_shortcut_button(event):
            if event.obj.name == "Last year":
                self.start_pubdate_input.value, self.end_pubdate_input.value = (
                    str(datetime.now().year),
                    str(datetime.now().year),
                )
            elif event.obj.name == "Past 5 years":
                self.start_pubdate_input.value, self.end_pubdate_input.value = (
                    str(datetime.now().year - 5),
                    str(datetime.now().year),
                )
            elif event.obj.name == "Past 10 years":
                self.start_pubdate_input.value, self.end_pubdate_input.value = (
                    str(datetime.now().year - 10),
                    str(datetime.now().year),
                )

        self.last_year_button.on_click(did_click_shortcut_button)
        self.past_5years_button.on_click(did_click_shortcut_button)
        self.past_10years_button.on_click(did_click_shortcut_button)

    def new_picker_title(self, entity, picker, values, options):
        value_count = len(picker.value)
        options_count = len(picker.options)

        if value_count == options_count:
            title = f"All {entity} ({ value_count })"

        elif value_count == 0:
            title = f"No {entity} (0 out of { options_count })"

        else:
            title = f"{ value_count } {entity} out of { options_count }"

        return title

    def get_sidebar(self):
        print("GET_SIDEBAR")

        items = [
            pn.pane.Markdown(
                "### Publication Details", css_classes=["filters-section-header"]
            ),
            pn.Column(
                pn.Row(self.start_pubdate_input, self.end_pubdate_input),
                self.pubdate_slider,
                pn.Row(
                    self.last_year_button,
                    self.past_5years_button,
                    self.past_10years_button,
                    css_classes=["years-buttons"],
                ),
            ),
            divider(),
            self.journal_select_picker,
            self.affiliation_country_select_picker,
            self.funder_select_picker,
            self.tags_select_picker,
        ]

        sidebar = pn.Column(*items)

        return sidebar

    def get_top_bar(self):
        print("GET_TOP_BAR")

        return pn.Row(
            pn.widgets.Select.from_param(self.param.extraction_tool),
            pn.widgets.Select.from_param(self.param.metrics),
            pn.widgets.Select.from_param(self.param.splitting_var),
        )

    def get_intro_block(self):
        add_intro_block = pn.pane.HTML(
            """
            <script type="text/javascript">
                const intro_block = document.createElement("div");
                intro_block.innerHTML = `
                    <div class="intro-block">
                        <h1>OpenSciMetrics Dashboard</h1>
                        <p>OpenSciMetrics is a tool designed to evaluate open science practices in biomedical publications, such as data sharing, code availability, and research transparency. Our goal is to provide insights into how these practices evolve over time and across different fields, journals, and countries. Use the dashboard below to explore key metrics and trends.</p>
                        <div class="intro-buttons">
                            <button class="explore-data-button">Explore the data</button>
                            <button class="learn-more-button">LEARN MORE</button>
                            <button class="github-button">GITHUB</button>
                        </div>
                    </div>
                `;
                console.log(intro_block);
                console.log(document.querySelector('#header-design-provider'));
                document.querySelector('#header-design-provider').appendChild(intro_block);
            </script>
            """
        )
        print(add_intro_block)
        return add_intro_block

    def get_dashboard(self):
        print("GET_DASHBOARD")

        items = [
            self.get_top_bar(),
            divider(),
            self.echarts_pane,
            # self.get_intro_block(),
        ]

        if self.debug:
            items += [divider(), self.echarts_update_button, self.echarts_config_editor]

        # Layout the dashboard
        dashboard = pn.Column(
            *items,
            css_classes=["dashboard-column"],
        )

        return dashboard
