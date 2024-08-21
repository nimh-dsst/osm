import pandas as pd
import panel as pn
import param

pn.extension("echarts")


pd.options.display.max_columns = None

# filters = {
#     "journal" : "category",
#     "metrics" : "select",
# }


groups = {"year": "int"}


datasets_metrics = {
    "RTransparent": ["is_data_pred", "is_code_pred", "score", "eigenfactor_score"]
}

dims_aggregations = {
    "is_data_pred": ["percent", "count_true", "count"],
    "is_code_pred": ["percent", "count_true"],
    "score": ["mean"],
    "eigenfactor_score": ["mean"],
}


aggregation_formulas = {
    "percent": lambda x: x.mean() * 100,
    "count_true": lambda x: (x == True).sum(),  # noqa
    "count": "count",
    "mean": "mean",
}


class MainDashboard(param.Parameterized):
    """
    Main dashboard for the application.
    """

    # High-level parameters.
    dataset = param.Selector(default="", objects=[], label="Dataset")

    metrics = param.ListSelector(default=[], objects=[], label="Metrics")

    splitting_var = param.Selector(
        default="year",
        objects=["year", "fund_pmc_institute"],
        label="Splitting Variable",
    )

    # Filters
    filter_pubdate = param.Range(step=1, label="Publication date")

    filter_journal = param.Selector(
        default="All journals (including empty)",
        objects=[
            "All journals (including empty)",
            "All journals (excluding empty values)",
            "Only selected journals",
        ],
        label="Journal",
    )
    filter_selected_journals = param.ListSelector(default=[], objects=[], label="")

    def __init__(self, datasets, **params):
        super().__init__(**params)

        self.datasets = datasets

        # By default, take the first dataset.
        # Currently, there's only RTransparent
        self.param.dataset.objects = list(self.datasets.keys())
        self.dataset = self.param.dataset.objects[0]

    @pn.depends("dataset", watch=True)
    def did_change_dataset(self):
        self.metrics = datasets_metrics[self.dataset]
        self.raw_data = self.datasets[self.dataset]

        # Hardcoded for RTransparent for the moment, update to more generic later

        self.param.filter_pubdate.bounds = (
            self.raw_data.year.min(),
            self.raw_data.year.max(),
        )
        self.param.filter_pubdate.default = (
            self.raw_data.year.min(),
            self.raw_data.year.max(),
        )

        self.param.filter_selected_journals.objects = self.raw_data.journal.unique()
        # As default, takes the journals with the biggest number of occurences
        self.filter_selected_journals = list(
            self.raw_data.journal.value_counts().iloc[:10].index
        )

    def filtered_grouped_data(self):
        filters = []

        if self.filter_journal == "All journals (excluding empty values)":
            filters.append(("journal.notnull()"))
        elif self.filter_journal == "Only selected journals":
            filters.append(f"journal in {self.filter_selected_journals}")

        if self.filter_pubdate is not None:
            filters.append(f"year >= {self.filter_pubdate[0]}")
            filters.append(f"year <= {self.filter_pubdate[1]}")

        filtered_df = (
            self.raw_data.query(" and ".join(filters)) if filters else self.raw_data
        )

        aggretations = {}
        for field, aggs in dims_aggregations.items():
            for agg in aggs:
                aggretations[f"{agg}_{field}"] = (field, aggregation_formulas[agg])

        result = (
            filtered_df.groupby(self.splitting_var).agg(**aggretations).reset_index()
        )

        return result

    @pn.depends("dataset", "splitting_var", "filter_pubdate")
    def get_echart_plot(self):
        df = self.filtered_grouped_data()

        xAxis = df[self.splitting_var].tolist()
        series = [
            {
                "id": serie,
                "name": serie,
                "type": "line",
                "data": df[serie].tolist(),
            }
            for serie in ["percent_is_data_pred", "percent_is_code_pred"]
        ]

        echarts_config = {
            "title": {
                "text": "Percentage of Publications Following Open Science Practices Over Time",
            },
            "tooltip": {
                "show": True,
                "trigger": "axis",
                # "formatter": f"""<b>{self.splitting_var}</b> : {{b0}} <br />
                #                 {{a0}} : {{c0}} <br />
                #                 {{a1}} : {{c1}} """,
            },
            "legend": {
                #'data':['Sales']
                "data": ["is_data_pred", "is_code_pred"],
                "orient": "vertical",
                "right": 10,
                "top": 20,
                "bottom": 20,
                "show": True,
            },
            "xAxis": {
                "data": xAxis,
                "name": self.splitting_var,
                "nameLocation": "center",
                "nameGap": 30,
            },
            "yAxis": {
                "name": "percent",
                "nameLocation": "center",
                "nameGap": 30,
            },
            "series": series,
        }
        echarts_pane = pn.pane.ECharts(
            echarts_config, height=640, width=840, renderer="svg"
        )
        return echarts_pane

    # Below are all the functions returning the different parts of the dashboard :
    # Sidebar, Top Bar and the plot area (in function get_dashboard)

    @pn.depends("filter_pubdate.bounds")
    def get_pubdate_filter(self):
        start_pubdate_input = pn.widgets.TextInput(
            value=str(int(self.param.filter_pubdate.bounds[0])), width=80
        )
        end_pubdate_input = pn.widgets.TextInput(
            value=str(int(self.param.filter_pubdate.bounds[1])), width=80
        )

        pubdate_slider = pn.widgets.RangeSlider.from_param(self.param.filter_pubdate)

        def update_pubdate_text_inputs(event):
            start_pubdate_input.value = str(pubdate_slider.value[0])
            end_pubdate_input.value = str(pubdate_slider.value[1])

        pubdate_slider.param.watch(update_pubdate_text_inputs, "value")

        def update_pubdate_slider(event):
            pubdate_slider.value = (
                int(start_pubdate_input.value or self.param.filter_pubdate.bounds[0]),
                int(end_pubdate_input.value or self.param.filter_pubdate.bounds[1]),
            )

        start_pubdate_input.param.watch(update_pubdate_slider, "value")
        end_pubdate_input.param.watch(update_pubdate_slider, "value")

        return pn.Column(pn.Row(start_pubdate_input, end_pubdate_input), pubdate_slider)

    @pn.depends("dataset", "filter_journal")
    def get_sidebar(self):
        items = [
            pn.pane.Markdown("## Filters"),
            pn.pane.Markdown("### Applied Filters"),
            pn.pane.Markdown("(todo)"),
            pn.layout.Divider(),
            pn.pane.Markdown("### Publication Details"),
            # pn.pane.Markdown("#### Publication Date"),
            self.get_pubdate_filter,
            pn.layout.Divider(),
            pn.widgets.Select.from_param(self.param.filter_journal),
        ]

        if self.filter_journal == "Only selected journals":
            items.append(
                pn.widgets.MultiChoice.from_param(
                    self.param.filter_selected_journals, max_items=10
                )
            )

        sidebar = pn.Column(*items)

        return sidebar

    @pn.depends("dataset")
    def get_top_bar(self):
        return pn.Row(
            pn.widgets.Select.from_param(self.param.dataset),
            pn.widgets.CheckBoxGroup.from_param(self.param.metrics),
            pn.widgets.Select.from_param(self.param.splitting_var),
        )

    @pn.depends(
        "dataset", "filter_journal", "filter_selected_journals", "splitting_var"
    )
    def get_dashboard(self):
        # Layout the dashboard
        dashboard = pn.Column(
            "# Data and code transparency",
            pn.Column(
                self.get_top_bar, self.get_echart_plot, sizing_mode="stretch_width"
            ),
        )

        return dashboard
