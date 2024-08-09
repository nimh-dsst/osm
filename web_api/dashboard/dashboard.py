import hmac

import pandas as pd
import plotly.express as px
import streamlit as st


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


# Function to load data with the new caching mechanism
@st.cache_data
def load_data():
    return pd.read_parquet("data/all_ics.parquet")


# Function to plot bar chart
def plot_bar_chart(data, x, y, hover_data, title):
    fig = px.bar(data, x=x, y=y, hover_data=hover_data, labels={y: title, x: ""})
    fig.update_traces(marker_color=st.get_option("theme.primaryColor"))
    fig.update_layout(
        xaxis={"categoryorder": "total descending"},
        xaxis_showticklabels=False,
        title=title,
        plot_bgcolor=st.get_option("theme.backgroundColor"),
        paper_bgcolor=st.get_option("theme.backgroundColor"),
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


if not check_password():
    st.stop()

# Load data
data = load_data()

# Page selection
page = st.sidebar.selectbox("Select a Page:", ["PI Data", "IC Data"])

if page == "PI Data":
    # Filters for PI Data page
    st.sidebar.header("Filters")
    years = data["journal_year"].unique().tolist()
    ics = data["organization_name"].unique().tolist()
    year_choice = st.sidebar.multiselect("Year", years, default=years)
    ic_choice = st.sidebar.multiselect("IC (Organization)", ics, default=ics)

    # Filtering data for PI Data page
    filtered_data = data[
        (data["journal_year"].isin(year_choice))
        & (data["organization_name"].isin(ic_choice))
    ]

    # Grouping data for PI Data page
    grouped_data = (
        filtered_data.groupby("contact_pi_project_leader")
        .agg(
            num_pmids=("pmid", "size"),
            num_unique_pmids=("pmid", pd.Series.nunique),
            proportion_pmids_open=(
                "pmid",
                lambda x: (
                    x[filtered_data["open_data"]].nunique() / x.nunique()
                    if x.nunique() > 0
                    else 0
                ),
            ),
        )
        .reset_index()
    )

    # Sorting the grouped data for better visualization for PI Data page
    grouped_data = grouped_data.sort_values("num_unique_pmids", ascending=False)

    # Display the table for PI Data page
    st.write("Filtered Data", grouped_data)

    # Plotting for PI Data page
    plot_bar_chart(
        grouped_data,
        "contact_pi_project_leader",
        "num_unique_pmids",
        ["contact_pi_project_leader", "num_unique_pmids"],
        "Number of Unique PMIDs",
    )
    plot_bar_chart(
        grouped_data,
        "contact_pi_project_leader",
        "proportion_pmids_open",
        ["contact_pi_project_leader", "proportion_pmids_open"],
        "Proportion of Open Data PMIDs",
    )

elif page == "IC Data":
    # Filters for IC Data page
    st.sidebar.header("Filters")
    years = data["journal_year"].unique().tolist()
    year_choice = st.sidebar.multiselect("Year", years, default=years)

    # Filtering data for IC Data page
    filtered_data = data[(data["journal_year"].isin(year_choice))]

    # Grouping data for IC Data page
    grouped_data_ic = (
        filtered_data.groupby("organization_name")
        .agg(
            num_pmids=("pmid", "size"),
            num_unique_pmids=("pmid", pd.Series.nunique),
            proportion_pmids_open=(
                "pmid",
                lambda x: (
                    x[filtered_data["open_data"]].nunique() / x.nunique()
                    if x.nunique() > 0
                    else 0
                ),
            ),
        )
        .reset_index()
    )

    # Sorting the grouped data for better visualization for IC Data page
    grouped_data_ic = grouped_data_ic.sort_values("num_unique_pmids", ascending=False)

    # Display the table for IC Data page
    st.write("Filtered Data by IC", grouped_data_ic)

    # Plotting for IC Data page
    plot_bar_chart(
        grouped_data_ic,
        "organization_name",
        "num_unique_pmids",
        ["organization_name", "num_unique_pmids"],
        "Number of Unique PMIDs",
    )
    plot_bar_chart(
        grouped_data_ic,
        "organization_name",
        "proportion_pmids_open",
        ["organization_name", "proportion_pmids_open"],
        "Proportion of Open Data PMIDs",
    )
