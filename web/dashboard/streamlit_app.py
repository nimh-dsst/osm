"""Usage:

    LOCAL_DATA_PATH=big_files/matches.parquet streamlit run streamlit_app.py

Make sure you have Streamlit, Polars, and Plotly installed. Current versions:

- Streamlit: 1.47.1
- Polars: 1.32.0
- Plotly: 6.2.0
"""

import os

import plotly.express as px  # type: ignore[attr-defined]
import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

MIN_YEAR = 2000
NIH_INSTITUTES_AND_FUNDERS = [
    "National Cancer Institute",
    "National Eye Institute",
    "National Heart Lung and Blood Institute",
    "National Human Genome Research Institute",
    "National Institute on Aging",
    "National Institute on Alcohol Abuse and Alcoholism",
    "National Institute of Allergy and Infectious Diseases",
    "National Institute of Arthritis and Musculoskeletal and Skin Diseases",
    "National Institute of Biomedical Imaging and Bioengineering",
    "National Institute of Child Health and Human Development",
    "National Institute on Deafness and Other Communication Disorders",
    "National Institute of Dental and Craniofacial Research",
    "National Institute of Diabetes and Digestive and Kidney Diseases",
    "National Institute on Drug Abuse",
    "National Institute of Environmental Health Sciences",
    "National Institute of General Medical Sciences",
    "National Institute of Mental Health",
    "National Institute on Minority Health and Health Disparities",
    "National Institute of Neurological Disorders and Stroke",
    "National Institute of Nursing Research",
    "National Library of Medicine",
    "NIH Clinical Center",
    "Center for Information Technology",
    "Center for Scientific Review",
    "Fogarty International Center",
    "National Center for Advancing Translational Sciences",
    "National Center for Complementary and Integrative Health",
]
FUNDER_ACRONYMS = {
    "National Institutes of Health": "NIH",
    "European Commission": "EC",
    "National Natural Science Foundation of China": "NSFC",
    "German Research Foundation": "DFG",
    "Japan Agency for Medical Research and Development": "AMED",
    "Wellcome Trust": "WT",
    "Canadian Institutes of Health Research": "CIHR",
    "Medical Research Council": "MRC",
    "Howard Hughes Medical Institute": "HHMI",
    "Bill & Melinda Gates Foundation": "BMGF",
    "National Cancer Institute": "NCI",
    "National Institute of Allergy and Infectious Diseases": "NIAID",
    "National Institute on Aging": "NIA",
    "National Heart Lung and Blood Institute": "NHLBI",
    "National Institute of General Medical Sciences": "NIGMS",
    "National Institute of Neurological Disorders and Stroke": "NINDS",
    "National Institute of Diabetes and Digestive and Kidney Diseases": "NIDDK",
    "National Institute of Mental Health": "NIMH",
    "National Institute of Child Health and Human Development": "NICHD",
    "National Institute on Drug Abuse": "NIDA",
    "National Institute of Environmental Health Sciences": "NIEHS",
    "National Eye Institute": "NEI",
    "National Human Genome Research Institute": "NHGRI",
    "National Institute of Arthritis and Musculoskeletal and Skin Diseases": "NIAMS",
    "National Institute on Alcohol Abuse and Alcoholism": "NIAAA",
    "National Institute of Dental and Craniofacial Research": "NIDCR",
    "National Library of Medicine": "NLM",
    "National Institute of Biomedical Imaging and Bioengineering": "NIBIB",
    "National Institute on Minority Health and Health Disparities": "NIMHD",
    "National Institute of Nursing Research": "NINR",
    "National Center for Complementary and Integrative Health": "NCCIH",
}
REVERSE_FUNDER_ACRONYMS = {v: k for k, v in FUNDER_ACRONYMS.items()}

try:
    PATH = os.environ["LOCAL_DATA_PATH"]
except KeyError:
    msg = "LOCAL_DATA_PATH environment variable not found, please set it."
    raise RuntimeError(msg)

row_1_col_1, row_1_col_2, row_1_col_3 = st.columns(3)
row_2_col_1, row_2_col_2, row_2_col_3 = st.columns(3)

with row_1_col_1:
    splitting_variable: str | None = st.selectbox(
        "Splitting variable",
        options=[None, "Journal", "Affiliation Country", "Funder"],
        index=3,  # default to 'funder'
    )
    if splitting_variable is not None:
        splitting_variable = splitting_variable.lower().replace(" ", "_")
with row_1_col_2:
    aggregation_name = st.selectbox(
        "Aggregation",
        options=[
            "Data Sharing Percent",
            "Data Sharing",
            "Count",
            "Code Sharing Percent",
            "Code Sharing",
        ],
        index=0,
    )
    aggregation_name = aggregation_name.lower().replace(" ", "_")
with row_1_col_3:
    y_axis_sort_method = st.selectbox(
        "Y-axis sort method",
        ["Alphabetic", "Last aggregated value", "Median aggregated value"],
        index=1,
    )


@st.cache_resource
def load_data() -> pl.DataFrame:
    return (
        pl.scan_parquet(PATH)  # pyright: ignore[reportUnknownMemberType]
        .select(
            "is_open_data",
            "is_open_code",
            "affiliation_country",
            "journal",
            "funder",
            "year",
        )
        .filter(pl.col("year") >= MIN_YEAR)
        .collect()
    )


@st.cache_resource
def load_data_for_funder() -> pl.DataFrame:
    return (
        pl.scan_parquet(PATH)  # pyright: ignore[reportUnknownMemberType]
        .select(
            "is_open_data",
            "is_open_code",
            "affiliation_country",
            "journal",
            "funder",
            "year",
        )
        .filter(pl.col("year") >= MIN_YEAR)
        .with_columns(pl.col("funder").list.unique())
        .explode("funder")
        .filter(
            pl.col("funder").str.len_chars() > 0,
            pl.col("funder").is_not_null(),
        )
        .collect()
    )


@st.cache_resource
def load_data_for_country() -> pl.DataFrame:
    return (
        pl.scan_parquet(PATH)  # pyright: ignore[reportUnknownMemberType]
        .select(
            "is_open_data",
            "is_open_code",
            "affiliation_country",
            "journal",
            "funder",
            "year",
        )
        .filter(
            pl.col("year") >= MIN_YEAR,
            pl.col("affiliation_country").is_not_null(),
        )
        .with_columns(pl.col("affiliation_country").str.split("; ").list.unique())
        .explode("affiliation_country")
        .filter(
            pl.col("affiliation_country").str.len_chars() > 0,
            pl.col("affiliation_country").is_not_null(),
        )
        .collect()
    )


data = load_data()
data_for_country = load_data_for_country()
data_for_funder = load_data_for_funder()


unique_journals = data["journal"].unique(maintain_order=True).to_list()
if splitting_variable == "journal":
    default_journals = (
        data.group_by("journal")
        .len()
        .select(pl.col("journal").top_k_by("len", 10))["journal"]
        .to_list()
    )
else:
    default_journals = []
with row_2_col_1:
    journals = st.multiselect(
        "Journal", options=unique_journals, default=default_journals
    )

unique_countries = (
    data_for_country["affiliation_country"].unique(maintain_order=True).to_list()
)
if splitting_variable == "affiliation_country":
    default_countries = (
        data_for_country.group_by("affiliation_country")
        .len()
        .select(pl.col("affiliation_country").top_k_by("len", 10))[
            "affiliation_country"
        ]
        .to_list()
    )
else:
    default_countries = []
with row_2_col_2:
    countries = st.multiselect(
        "Country",
        options=unique_countries,
        default=default_countries,
    )

unique_funders = data_for_funder["funder"].unique(maintain_order=True).to_list()
if splitting_variable == "funder":
    funders_preset = st.selectbox(
        "Funders preset",
        options=["Top funders", "NIH institutes and funders"],
        index=0,
    )
    if funders_preset == "Top funders":
        # Ensure that Howard Hughes Medical Institute always appears.
        default_funders: list[str] = (
            data_for_funder.group_by("funder")
            .len()
            .filter(~pl.col("funder").is_in(NIH_INSTITUTES_AND_FUNDERS))
            .select(pl.col("funder").top_k_by("len", 10))["funder"]
            .to_list()
        )
        if "Howard Hughes Medical Institute" not in default_funders:
            default_funders = [
                *data_for_funder.group_by("funder")
                .len()
                .filter(pl.col("funder").is_in(NIH_INSTITUTES_AND_FUNDERS))
                .select(pl.col("funder").top_k_by("len", 10))["funder"]
                .to_list(),
                "Howard Hughes Medical Institute",
            ]
    else:
        default_funders = set(NIH_INSTITUTES_AND_FUNDERS).intersection(unique_funders)
else:
    default_funders = []

with row_2_col_3:
    funders = st.multiselect(
        "Funder",
        options=[FUNDER_ACRONYMS.get(x, x) for x in unique_funders],
        default=[FUNDER_ACRONYMS.get(x, x) for x in default_funders],
    )

max_year: int = data["year"].max()  # type: ignore[assignment]
years: tuple[int, int] = st.slider(  # type: ignore[assignment]
    "Years",
    min_value=MIN_YEAR,
    max_value=max_year,
    value=(MIN_YEAR, max_year),
)

FORMULAE = {
    "data_sharing_percent": pl.col("is_open_data").mean() * 100,
    "data_sharing": pl.col("is_open_data").sum(),
    "count": pl.col("is_open_data").len(),
    "code_sharing_percent": pl.col("is_open_code").mean() * 100,
    "code_sharing": pl.col("is_open_code").sum(),
}
formula = FORMULAE[aggregation_name]


def apply_filters(df: pl.DataFrame) -> pl.DataFrame:
    df = df.filter(pl.col("year").is_between(*years, closed="both"))
    if journals:
        df = df.filter(pl.col("journal").is_in(journals))
    if countries:
        if splitting_variable == "affiliation_country":
            # 'affiliation_country' has already been preprocessed, so we can just use `is_in`.
            df = df.filter(pl.col("affiliation_country").is_in(countries))
        else:
            df = df.filter(
                pl.any_horizontal(
                    [
                        pl.col("affiliation_country").str.split("; ").list.contains(x)
                        for x in countries
                    ],
                ),
            )
    if funders:
        full_name_funders: list[str | None] = [
            REVERSE_FUNDER_ACRONYMS.get(x, x) if x else None for x in funders
        ]
        if splitting_variable == "funder":
            # 'funder' has already been preprocessed, so we can just use `is_in`.
            df = df.filter(pl.col("funder").is_in(full_name_funders))
        else:
            df = df.filter(
                pl.any_horizontal(
                    [pl.col("funder").list.contains(x) for x in full_name_funders]
                ),
            )
    return df


def sort_for_y_axis(df: pl.DataFrame) -> pl.DataFrame:
    if y_axis_sort_method == "Alphabetic":
        return df.sort(
            splitting_variable,
            "year",
        )
    if y_axis_sort_method == "Last aggregated value":
        return df.sort(
            pl.col(aggregation_name).last().over(splitting_variable, order_by="year"),
            "year",
            descending=[True, False],
        )
    if y_axis_sort_method == "Median aggregated value":
        return df.sort(
            pl.col(aggregation_name).median().over(splitting_variable),
            "year",
            descending=[True, False],
        )
    msg = "Unreachable code"
    raise RuntimeError(msg)


if splitting_variable is None:
    df = apply_filters(data)
    summary = df.group_by("year").agg(formula.alias(aggregation_name)).sort("year")
    fig = px.line(  # pyright: ignore[reportUnknownMemberType]
        summary,
        x="year",
        y=aggregation_name,
        title="Open Data Over Time",
    )

elif splitting_variable == "journal":
    df = apply_filters(data)
    summary = (
        df.group_by(splitting_variable, "year")
        .agg(formula.alias(aggregation_name))
        .pipe(sort_for_y_axis)
    )
    fig = px.line(  # pyright: ignore[reportUnknownMemberType]
        summary,
        x="year",
        y=aggregation_name,
        color=splitting_variable,
        title=f"Open Data by {splitting_variable.title()} Over Time",
    )
else:
    df = data_for_funder if splitting_variable == "funder" else data_for_country
    df = apply_filters(df)
    summary = (
        df.select("is_open_data", "year", "is_open_code", splitting_variable)
        .group_by(splitting_variable, "year")
        .agg(formula.alias(aggregation_name))
        .pipe(sort_for_y_axis)
    )
    fig = px.line(  # pyright: ignore[reportUnknownMemberType]
        summary,
        x="year",
        y=aggregation_name,
        color=splitting_variable,
        title=f"Open Data by {splitting_variable.title()} Over Time",
    )

fig.update_layout(hovermode="x unified", height=600)  # pyright: ignore[reportUnknownMemberType]
if "percent" in aggregation_name:
    fig.update_traces(hovertemplate="%{y:,.1f}")  # pyright: ignore[reportUnknownMemberType]
else:
    fig.update_traces(hovertemplate="%{y}")  # pyright: ignore[reportUnknownMemberType]
st.plotly_chart(fig, use_container_width=True)  # pyright: ignore[reportUnknownMemberType]

st.text("Toggle lines on or off by clicking on them")
