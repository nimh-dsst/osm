"""Usage:

    LOCAL_DATA_PATH=big_files/matches.parquet streamlit run web/dashboard/streamlit_app.py

Make sure you have Streamlit, Polars, PyCountry, and Plotly installed. Current versions:

- Streamlit: 1.47.1
- Polars: 1.32.0
- Plotly: 6.2.0
- pycountry: 24.6.1
"""

import csv
import os
from pathlib import Path

import plotly.express as px  # type: ignore[attr-defined]
import polars as pl
import pycountry
import streamlit as st

st.set_page_config(layout="wide")

MIN_YEAR = 2000

# Funder normalization.
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
# Load funder to country mapping from CSV file
FUNDER_ALIASES_PATH = Path(__file__).parent / "data" / "funder_aliases_v3.csv"


def load_funder_countries() -> dict[str, str]:
    """Load funder to country mapping from the funder aliases CSV."""
    funder_countries: dict[str, str] = {}
    if FUNDER_ALIASES_PATH.exists():
        with open(FUNDER_ALIASES_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                canonical_name = row["canonical_name"]
                country = row["country"]
                if (
                    canonical_name
                    and country
                    and canonical_name not in funder_countries
                ):
                    funder_countries[canonical_name] = country
    return funder_countries


FUNDER_COUNTRIES: dict[str, str] = load_funder_countries()


# Country normalization.
RAW_REFERENCE_COUNTRIES: list[str] = [x.name.lower() for x in pycountry.countries]  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
COUNTRY_NORMALISATION = {
    "korea, republic of": "south korea",
    "korea": "south korea",
    "uk": "united kingdom",
    "ukuk": "united kingdom",
    "usa": "united states",
    "iran, islamic republic of": "iran",
    "taiwan, province of china": "taiwan",
    "russian federation": "russia",
    "türkiye": "turkey",
    "czechia": "czech republic",
    "viet nam": "vietnam",
    "tanzania, united republic of": "tanzania",
    "venezuela, bolivarian republic of": "venezuela",
    "south south korea": "south korea",
    "palestine, state of": "palestine",
    "côte d'ivoire": "ivory coast",
}
COUNTRY_NAME_FIXES: dict[str, str] = {
    **{x.alpha_2.lower(): x.name.lower() for x in (pycountry.countries)},  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
    **COUNTRY_NORMALISATION,
}
REFERENCE_COUNTRIES: list[str] = [
    COUNTRY_NORMALISATION.get(x, x).title() for x in RAW_REFERENCE_COUNTRIES
]


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
        options=[None, "Affiliation Country", "Funder"],
        index=2,  # default to 'funder'
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
        .with_columns(
            pl.col("affiliation_country")
            .str.to_lowercase()
            .str.split("; ")
            .list.eval(pl.element().replace(COUNTRY_NAME_FIXES).str.to_titlecase())
        )
        .filter(pl.col("year") >= MIN_YEAR)
        .collect()
    )


@st.cache_resource
def load_data_for_funder() -> pl.DataFrame:
    return (
        load_data()  # pyright: ignore[reportUnknownMemberType]
        .select(
            "is_open_data",
            "is_open_code",
            "affiliation_country",
            "journal",
            "funder",
            "year",
        )
        .with_columns(pl.col("funder").list.unique(maintain_order=True))
        .explode("funder")
        .filter(
            pl.col("funder").str.len_chars() > 0,
            pl.col("funder").is_not_null(),
        )
    )


@st.cache_resource
def load_data_for_country() -> pl.DataFrame:
    return (
        load_data()
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
        .with_columns(pl.col("affiliation_country").list.unique(maintain_order=True))
        .explode("affiliation_country")
        .filter(
            pl.col("affiliation_country").is_in(REFERENCE_COUNTRIES),
            pl.col("affiliation_country").str.len_chars() > 0,
            pl.col("affiliation_country").is_not_null(),
        )
    )


data = load_data()
data_for_country = load_data_for_country()
data_for_funder = load_data_for_funder()


# Journal functionality temporarily disabled due to compute constraints
journals: list[str] = []
with row_2_col_1:
    st.multiselect(
        "Journal (disabled)",
        options=[],
        default=[],
        key="journal",
        disabled=True,
        help="Journal filtering is temporarily disabled due to the large number of journals.",
    )


def get_unique_countries() -> list[str]:
    df = load_data_for_country()
    return sorted(
        df["affiliation_country"]
        .value_counts()
        # Exclude countries that appear fewer than 100 times. Many of these are typos or city names.
        .filter(pl.col("count") >= 100)["affiliation_country"]
        .to_list()
    )


unique_countries = get_unique_countries()
if splitting_variable == "affiliation_country":
    default_countries: list[str] = (
        data_for_country.group_by("affiliation_country")
        .len()
        .top_k(10, by="len")
        .sort("len")["affiliation_country"]
        .to_list()
    )
else:
    default_countries = []
with row_2_col_2:
    countries = st.multiselect(
        "Country",
        options=unique_countries,
        default=default_countries,
        key="country",
    )

unique_funders = sorted(data_for_funder["funder"].unique(maintain_order=True).to_list())


def get_default_funders_by_metrics() -> list[str]:
    """Get top 5 funders by Data Sharing Percent + top 5 by Data Sharing count."""
    # Calculate data sharing percent for each funder
    funder_stats = (
        data_for_funder.group_by("funder")
        .agg(
            (pl.col("is_open_data").mean() * 100).alias("data_sharing_percent"),
            pl.col("is_open_data").sum().alias("data_sharing_count"),
        )
        .filter(pl.col("funder").is_not_null())
    )

    # Top 5 by data sharing percent
    top_by_percent = funder_stats.top_k(5, by="data_sharing_percent")[
        "funder"
    ].to_list()

    # Top 5 by data sharing count
    top_by_count = funder_stats.top_k(5, by="data_sharing_count")["funder"].to_list()

    # Combine and deduplicate, preserving order
    combined = []
    for f in top_by_percent + top_by_count:
        if f not in combined:
            combined.append(f)

    return combined


if splitting_variable == "funder":
    funders_preset = st.selectbox(
        "Funders preset",
        options=["Top by data sharing"],
        index=0,
        disabled=True,
        help="Additional presets coming soon",
    )
    # Top 5 by Data Sharing Percent + top 5 by Data Sharing count
    default_funders: list[str] = get_default_funders_by_metrics()
else:
    default_funders = []

with row_2_col_3:
    funders = st.multiselect(
        "Funder",
        options=unique_funders,  # Use full names, no acronyms
        default=default_funders,
        key="funder",
    )

max_year: int = data["year"].max()  # type: ignore[assignment]
DEFAULT_START_YEAR = 2010
DEFAULT_END_YEAR = 2024
years: tuple[int, int] = st.slider(  # type: ignore[assignment]
    "Years",
    min_value=MIN_YEAR,
    max_value=max_year,
    value=(DEFAULT_START_YEAR, min(DEFAULT_END_YEAR, max_year)),
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
                    [pl.col("affiliation_country").list.contains(x) for x in countries],
                ),
            )
    if funders:
        if splitting_variable == "funder":
            # 'funder' has already been preprocessed, so we can just use `is_in`.
            df = df.filter(pl.col("funder").is_in(funders))
        else:
            df = df.filter(
                pl.any_horizontal([pl.col("funder").list.contains(x) for x in funders]),
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

    # For funder view, add country to the legend labels
    if splitting_variable == "funder":
        # Create a new column with funder name + country for legend
        summary = summary.with_columns(
            pl.col("funder")
            .map_elements(
                lambda x: f"{x} ({FUNDER_COUNTRIES.get(x, 'Unknown')})",
                return_dtype=pl.Utf8,
            )
            .alias("funder_with_country")
        )
        fig = px.line(  # pyright: ignore[reportUnknownMemberType]
            summary,
            x="year",
            y=aggregation_name,
            color="funder_with_country",
            title="Open Data by Funder Over Time",
        )
    else:
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
