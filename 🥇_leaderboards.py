import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from supabase import create_client

favicon = Image.open("assets/abstract_square_300dpi.png")

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=favicon,
    page_title="abstract",
)
st.sidebar.image(Image.open("assets/abstract_05x.png"))


# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)


supabase = init_connection()

# # Perform query.
# @st.cache(allow_output_mutation=True)
# def run_query(table):
#     rows = supabase.table(table).execute()
#     res = pd.DataFrame(rows.data)
#     st.write(len(res))
#     return res


@st.cache(ttl=60 * 5)
def load_all_stats(season, variant):
    """ """
    table = "d1_" + variant + "_" + str(season)
    rows = supabase.table(table).select("*").execute()
    res = pd.DataFrame(rows.data)
    return res


def load_season_stats(season, variant, school, minimum, class_year):
    df = load_all_stats(season, variant)
    if school != "all":
        df = df.loc[df.school == school]
    # if position != "all":
    #     df = df.loc[df.position == position]
    if minimum > 0:
        if variant == "batting":
            df = df.loc[df.PA >= minimum]
        else:
            df = df.loc[df.IP >= minimum]
    if class_year != "all":
        if "other" == class_year:
            class_year == "N/A"
        df = df.loc[df.Yr == class_year]
    if variant == "batting":
        df = df[
            [
                "name",
                "Yr",
                "school",
                "PA",
                "H",
                "2B",
                "3B",
                "HR",
                "RBI",
                "R",
                "BB",
                "IBB",
                "HBP",
                "SF",
                "SH",
                "K",
                "GP",
                "AB",
                "1B",
                "wOBA",
                "OPS",
                "OBP",
                "SLG",
                "BA",
                "ISO",
                "BABIP",
                "HR/PA",
                "K/PA",
                "BB/PA",
                "wRAA",
                "wRC",
            ]
        ]
    else:
        df = df[
            [
                "name",
                "Yr",
                "school",
                "BF",
                "IP",
                "FIP",
                "ERA",
                "WHIP",
                "SO",
                "BB",
                "H",
                "HR-A",
                "ER",
                "R",
                "OPS-against",
                "OBP-against",
                "SLG-against",
                "BA-against",
                "K/PA",
                "K/9",
                "BB/PA",
                "BB/9",
                "HR-A/PA",
                "BABIP-against",
                "Pitches/PA",
                "IP/App",
                "App",
                "HB",
                "GO",
                "FO",
                "W",
                "L",
                "SV",
            ]
        ]
    return df


# IMPORTANT: Cache the conversion to prevent computation on every rerun
@st.cache(persist=True)
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


def load_school_options():
    rows = supabase.table("schools").select("*").eq("division", 1).execute()
    df = pd.DataFrame(rows.data)
    options = list(df.ncaa_name)
    options.insert(0, "all")
    return options


def create_dist(df, metric, season, minimum, min_type):
    fig = px.histogram(
        df,
        x=metric,
        marginal="box",
        hover_name="name",
        template="seaborn",
        color_discrete_sequence=['indianred']
    )
    fig.update_layout(
        title=str(season)
        + " "
        + metric
        + " distribution, min "
        + str(minimum)
        + " "
        + min_type,
        title_yanchor="top",
        title_x=0.5,
        xaxis_title=metric,
        yaxis_title="# of players",
    )
    return fig


col1, col2, col3, col4, col5, col6 = st.columns(6)
season = col1.selectbox(
    "Season", options=reversed(range(2013, 2023)), index=0, key="season_select"
)
variant = col5.selectbox(
    "Stats Type", options=["batting", "pitching"], index=0, key="variant_select"
)
class_year = col4.selectbox(
    "Class Year",
    options=["all", "Fr", "So", "Jr", "Sr", "other"],
    index=0,
    key="class_year_select",
)
if variant == "batting":
    position = col3.selectbox(
        "Position",
        options=["all", "INF", "OF", "C", "P", "DH"],
        index=0,
        key="position_select",
    )
    minimum = col6.number_input("Min. PA", min_value=0, value=100, step=1)
else:
    position = col3.selectbox(
        "Position", options=["all", "P", "notP"], index=0, key="position_select"
    )
    minimum = col6.number_input("Min. IP", min_value=0, value=10, step=1)

school = col2.selectbox(
    "School", options=load_school_options(), index=0, key="school_select"
)
stats = load_season_stats(season, variant, school, minimum, class_year)

if variant == "batting":
    counting_stats = stats[
        [
            "name",
            "Yr",
            "school",
            "PA",
            "H",
            "2B",
            "3B",
            "HR",
            "K",
            "BB",
            "R",
            "RBI",
            "IBB",
            "SF",
            "SH",
            "HBP",
        ]
    ].sort_values(by="H", ascending=False)
    counting_slice = [
        "PA",
        "H",
        "2B",
        "3B",
        "HR",
        "BB",
        "K",
        "IBB",
        "HBP",
        "RBI",
        "R",
        "SF",
        "SH",
    ]
    rate_stats = stats[
        [
            "name",
            "Yr",
            "school",
            "PA",
            "wOBA",
            "wRC",
            "wRAA",
            "OPS",
            "OBP",
            "SLG",
            "BA",
            "ISO",
            "BABIP",
            "K/PA",
            "BB/PA",
            "HR/PA",
        ]
    ].sort_values(by="wOBA", ascending=False)
    rate_slice = [
        "PA",
        "wOBA",
        "wRC",
        "wRAA",
        "OPS",
        "OBP",
        "SLG",
        "BA",
        "BABIP",
        "ISO",
        "K/PA",
        "BB/PA",
        "HR/PA",
    ]
    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Counting Stats")
    counting_stats_csv = convert_df(counting_stats)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=counting_stats_csv,
        file_name=str(season)
        + "_"
        + variant
        + "_counting_stat_leaders_batting"
        + "_"
        + str(position)
        + "_"
        + str(school)
        + "_minPA_"
        + str(minimum)
        + ".csv",
        mime="text/csv",
    )
    col3.write("")
    st.dataframe(
        counting_stats.style.highlight_max(
            axis=0,
            props="color:white; font-weight:bold; background-color:#aa3a3d;",
            subset=counting_slice,
        )
    )
    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Rate Stats")
    rate_stats_csv = convert_df(rate_stats)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=rate_stats_csv,
        file_name=str(season)
        + "_"
        + variant
        + "_rate_stat_leaders_batting"
        + "_"
        + str(position)
        + "_"
        + str(school)
        + "_minPA_"
        + str(minimum)
        + ".csv",
        mime="text/csv",
    )
    col3.write('')
    st.dataframe(
        rate_stats.style.format(
            {
                "PA": "{:.0f}",
                "wOBA": "{:.3f}",
                "wRC": "{:.1f}",
                "wRAA": "{:.1f}",
                "OPS": "{:.3f}",
                "OBP": "{:.3f}",
                "SLG": "{:.3f}",
                "BA": "{:.3f}",
                "BABIP": "{:.3f}",
                "ISO": "{:.3f}",
                "K/PA": "{:.3f}",
                "BB/PA": "{:.3f}",
                "HR/PA": "{:.3f}",
            },
            na_rep="",
            subset=rate_slice,
        ).highlight_max(
            axis=0,
            props="color:white; font-weight:bold; background-color:#aa3a3d;",
            subset=rate_slice,
        ),
        width=1000,
    )
    metric = st.selectbox(
        "select metric",
        options=[
            "PA",
            "H",
            "2B",
            "3B",
            "HR",
            "BB",
            "K",
            "IBB",
            "HBP",
            "RBI",
            "R",
            "SF",
            "SH",
            "wOBA",
            "wRC",
            "wRAA",
            "OPS",
            "OBP",
            "SLG",
            "BA",
            "BABIP",
            "ISO",
            "K/PA",
            "BB/PA",
            "HR/PA",
        ],
        index=13,
        key="metric_select",
    )
    st.plotly_chart(
        create_dist(stats, metric, season, minimum, "PA"), use_container_width=True
    )
else:
    rate_stats = stats[
        [
            "name",
            "Yr",
            "school",
            "IP",
            "BF",
            "ERA",
            "FIP",
            "WHIP",
            "K/PA",
            "BB/PA",
            "OPS-against",
            "OBP-against",
            "SLG-against",
            "BA-against",
            "BABIP-against",
            "Pitches/PA",
            "HR-A/PA",
            "IP/App",
        ]
    ]
    rate_slice = [
        "IP",
        "BF",
        "ERA",
        "FIP",
        "WHIP",
        "K/PA",
        "BB/PA",
        "OPS-against",
        "OBP-against",
        "SLG-against",
        "BA-against",
        "BABIP-against",
        "Pitches/PA",
        "HR-A/PA",
        "IP/App",
    ]
    counting_stats = stats[
        [
            "name",
            "Yr",
            "school",
            "IP",
            "BF",
            "App",
            "H",
            "SO",
            "BB",
            "ER",
            "R",
            "HR-A",
            "HB",
            "GO",
            "FO",
            "W",
            "L",
            "SV",
        ]
    ]
    counting_slice = [
        "IP",
        "BF",
        "App",
        "H",
        "SO",
        "BB",
        "ER",
        "R",
        "HR-A",
        "HB",
        "GO",
        "FO",
        "W",
        "L",
        "SV",
    ]
    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Counting Stats")
    counting_stats_csv = convert_df(counting_stats)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=counting_stats_csv,
        file_name=str(season)
        + "_"
        + variant
        + "_counting_stat_leaders_pitching"
        + "_"
        + str(position)
        + "_"
        + str(school)
        + "_minIP_"
        + str(minimum)
        + ".csv",
        mime="text/csv",
    )
    col3.write('')
    st.dataframe(
        counting_stats.style.highlight_max(
            axis=0,
            props="color:white; font-weight:bold; background-color:#aa3a3d;",
            subset=counting_slice,
        ).format({"IP": "{:.1f}"}),
        width=1000,
    )

    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Rate Stats")
    rate_stats_csv = convert_df(rate_stats)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=rate_stats_csv,
        file_name=str(season)
        + "_"
        + variant
        + "_rate_stat_leaders_pitching"
        + "_"
        + str(position)
        + "_"
        + str(school)
        + "_minPA_"
        + str(minimum)
        + ".csv",
        mime="text/csv",
    )
    col3.write('')
    st.dataframe(
        rate_stats.style.format(
            {
                "IP": "{:.1f}",
                "BF": "{:.0f}",
                "ERA": "{:.2f}",
                "FIP": "{:.3f}",
                "WHIP": "{:.3f}",
                "K/PA": "{:.3f}",
                "BB/PA": "{:.3f}",
                "OPS-against": "{:.3f}",
                "OBP-against": "{:.3f}",
                "BABIP-against": "{:.3f}",
                "SLG-against": "{:.3f}",
                "BA-against": "{:.3f}",
                "Pitches/PA": "{:.3f}",
                "HR-A/PA": "{:.3f}",
                "IP/App": "{:.3f}",
            },
            na_rep="",
            subset=rate_slice,
        )
    )
    metric = st.selectbox(
        "select metric",
        options=[
            "IP",
            "BF",
            "App",
            "H",
            "SO",
            "BB",
            "ER",
            "R",
            "HR-A",
            "HB",
            "GO",
            "FO",
            "W",
            "L",
            "SV",
            "ERA",
            "FIP",
            "WHIP",
            "K/PA",
            "BB/PA",
            "OPS-against",
            "OBP-against",
            "SLG-against",
            "BA-against",
            "BABIP-against",
            "Pitches/PA",
            "HR-A/PA",
            "IP/App",
        ],
        index=17,
        key="metric_select",
    )
    st.plotly_chart(
        create_dist(stats, metric, season, minimum, "IP"), use_container_width=True
    )
st.write("")
st.info(
    "Data from stats.ncaa.org. Linear Weights courtesy of Robert Frey."
)
