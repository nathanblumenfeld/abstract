import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
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


@st.cache(persist=True)
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode("utf-8")


@st.cache(ttl=60 * 5)
def load_season_stats(season, variant):
    """ """
    df = pd.read_parquet(
        "data/"
        + variant
        + "_stats_all_"
        + str(season)
        + "_percentiles_position_min20.parquet"
    )
    return df


def load_team_stats(df, school):
    return df.loc[df.school == school]


# @st.cache(ttl=60 * 5)
# def load_school_lookup():
#     return pd.read_parquet("collegebaseball/data/team_seasons.parquet")


@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)


supabase = init_connection()


@st.cache(persist=True, ttl=60 * 5)
def load_school_options():
    rows = supabase.table("schools").select("*").eq("division", 1).execute()
    df = pd.DataFrame(rows.data)
    res = df.ncaa_name.unique()
    return res


@st.cache(ttl=60 * 2)
def load_team_totals(school, season, variant):
    table = "d1_" + variant + "_totals_" + str(season)
    rows = (
        supabase.table(table)
        .select("*")
        .eq("division", 1)
        .eq("school", school)
        .execute()
    )
    df = pd.DataFrame(rows.data)
    return df


def create_histogram(data, metric, school, season):
    fig = px.histogram(
        data,
        x=metric,
        color="pos",
        marginal="rug",
        nbins=50,
        hover_name="name",
        template="seaborn",
        color_discrete_sequence=["#003f5c", "#7a5195", "#ef5675", "#ffa600"],
    )
    fig.update_layout(
        title=str(school) + " single-season " + metric + "'s, " + str(season),
        title_yanchor="top",
        title_x=0.5,
        xaxis_title=metric,
        yaxis_title="",
    )
    return fig


def create_dotplot(df, school, season, metrics):
    """ """
    fig = go.Figure()
    for i in metrics.keys():
        fig.add_trace(
            go.Scatter(
                x=df[i],
                y=df["name"],
                marker=dict(color=metrics[i], size=12),
                mode="markers",
                name=i,
            )
        )
    fig.update_layout(
        title=str(school) + ", " + str(season),
        xaxis=dict(showgrid=False, showline=True, zerolinecolor="DarkSlateGrey"),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor="DarkSlateGrey"),
        height=(len(df.name.unique()) * 45) + 100,
    )
    return fig


def create_scatter(data, metric1, metric2, metric3, metric4, school, season):
    fig = px.scatter(
        data,
        x=metric1,
        y=metric2,
        hover_name="name",
        size=metric3,
        color=metric4,
        color_discrete_sequence=["#003f5c", "#7a5195", "#ef5675", "#ffa600"],
    )
    fig.update_layout(
        title=str(school)
        + " "
        + str(season)
        + ", "
        + str(metric2)
        + " vs "
        + str(metric1)
        + "<br><sub>size="
        + str(metric3)
        + "</sub>",
        title_yanchor="top",
        title_x=0.5,
        xaxis_title=str(metric1),
        yaxis_title=str(metric2),
    )
    return fig


school_options = load_school_options()
col1, col2, col3 = st.columns([3, 2, 2])
school = col1.selectbox("School", options=school_options, index=55, key="team_school")
season = col2.selectbox("Season", options=range(2013, 2023), index=9, key="team_season")
variant = col3.selectbox(
    "Stats Type", options=["batting", "pitching"], key="team_stats_type"
)
stats = load_season_stats(season, variant)
totals = load_team_totals(school, season, variant)
team_for = totals.loc[totals.name == "Totals"]
team_vs = totals.loc[totals.name == "Opponent Totals"]
st.markdown('## Team Totals')
col1, col2, col3, col4= st.columns([1, 1, 1, 1])
if variant == "pitching":
    col1.metric(label="ERA", value=team_for["ERA"])
    col2.metric(label="FIP", value=team_for["FIP"])
    col3.metric(label="wOBA-against", value=team_for["wOBA-against"])
    col4.metric(label="OBP", value=team_for["OBP-against"])
elif variant == "batting":
    col1.metric(label="wOBA", value=team_for["wOBA"])
    col2.metric(label="OBP", value=team_for["OBP"])
    col3.metric(label="OPS", value=team_for["OPS"])
    col4.metric(label="BA", value=team_for["BA"])

# st.dataframe(totals, width=1000)
stats = load_team_stats(stats, school)
if variant == "batting":
    all_stats = stats
    rate_stats = all_stats[
        [
            "name",
            "Yr",
            "pos",
            "GP",
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
            "K%",
            "BB%",
            "HR%",
        ]
    ]
    counting_stats = all_stats[
        [
            "name",
            "Yr",
            "pos",
            "GP",
            "PA",
            "AB",
            "H",
            "1B",
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
    ]
    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Rate Stats")
    rate_stats_csv = convert_df(rate_stats)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=rate_stats_csv,
        file_name=str(school) + "_rate_stats_" + str(season) + ".csv",
        mime="text/csv",
    )
    col3.write('')
    rate_slice = [
        "GP",
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
        "K%",
        "BB%",
        "HR%",
    ]
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
                "K%": "{:,.2%}",
                "BB%": "{:,.2%}",
                "HR%": "{:,.2%}",
            },
            na_rep="",
            subset=rate_slice,
        )
    )
    percentiles = all_stats[
        [
            "name",
            "Yr",
            "pos",
            "PA",
            "wOBA-percentile",
            "wRC-percentile",
            "OPS-percentile",
            "OBP-percentile",
            "SLG-percentile",
            "BA-percentile",
            "ISO-percentile",
            "BABIP-percentile",
            "K%-percentile",
            "BB%-percentile",
            "HR%-percentile",
        ]
    ]

    percentiles_slice = [
        "wOBA-percentile",
        "wRC-percentile",
        "OPS-percentile",
        "OBP-percentile",
        "SLG-percentile",
        "BA-percentile",
        "ISO-percentile",
        "BABIP-percentile",
        "K%-percentile",
        "BB%-percentile",
        "HR%-percentile",
    ]

    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Percentiles")
    percentiles_csv = convert_df(percentiles)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=rate_stats_csv,
        file_name=str(school) + "_percentiles_min20PA" + str(season) + ".csv",
        mime="text/csv",
    )
    col3.write('')
    st.dataframe(
        percentiles.style.background_gradient(
            vmin=0,
            vmax=100,
            cmap=sns.color_palette("vlag", as_cmap=True),
            subset=percentiles_slice,
        )
            )
    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Counting Stats")
    counting_stats_csv = convert_df(counting_stats)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=counting_stats_csv,
        file_name=str(school) + "_counting_stats_" + str(season) + ".csv",
        mime="text/csv",
    )
    col3.write('')
    counting_slice = [
        "PA",
        "GP",
        "AB",
        "H",
        "1B",
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
    st.dataframe(counting_stats, width=1000)
    st.write("")
    rate_metrics = {
        "BB%": "#282A3E",
        "K%": "#147DF5",
        "BA": "#7C48AD",
        "OBP": "#AF125A",
        "wOBA": "#F7A072",
        "SLG": "#747274",
    }
    st.plotly_chart(
        create_dotplot(all_stats, school, season, rate_metrics),
        use_container_width=True,
    )
    st.write("")
else:
    all_stats = stats
    rate_stats = all_stats[
        [
            "name",
            "Yr",
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
    counting_stats = all_stats[
        [
            "name",
            "Yr",
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
            "2B-A",
            "3B-A",
            "GO",
            "FO",
            "W",
            "L",
            "SV",
        ]
    ]
    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Rate Stats")
    rate_stats_csv = convert_df(rate_stats)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=rate_stats_csv,
        file_name=str(school) + "_rate_stats_" + str(season) + ".csv",
        mime="text/csv",
    )
    col3.write('')
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
    percentiles = all_stats[
        [
            "name",
            "Yr",
            "pos",
            "IP",
            "BF",
            "FIP-percentile",
            "ERA-percentile",
            "WHIP-percentile",
            "OPS-against-percentile",
            "OBP-against-percentile",
            "SLG-against-percentile",
            "BA-against-percentile",
            "K/PA-percentile",
            "BB/PA-percentile",
            "HR-A/PA-percentile",
        ]
    ]
    percentiles_slice = [
        "FIP-percentile",
        "ERA-percentile",
        "WHIP-percentile",
        "OPS-against-percentile",
        "OBP-against-percentile",
        "SLG-against-percentile",
        "BA-against-percentile",
        "K/PA-percentile",
        "BB/PA-percentile",
        "HR-A/PA-percentile",
    ]
    col1, col2, col3 = st.columns([4, 2, 5])
    col1.markdown("## Percentiles")
    percentiles_csv = convert_df(percentiles)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=rate_stats_csv,
        file_name=str(school) + "_percentiles_min20BF_" + str(season) + ".csv",
        mime="text/csv",
    )
    col3.write('')
    st.dataframe(
        percentiles.style.background_gradient(
            vmin=0,
            vmax=100,
            cmap=sns.color_palette("vlag_r", as_cmap=True),
            subset=percentiles_slice,
        ).format({"IP": "{:.1f}"})
    )
    st.write("")
    col1, col2, col3 = st.columns([3, 2, 10])
    col1.markdown("## Counting Stats")
    counting_stats_csv = convert_df(counting_stats)
    col2.markdown("")
    col2.download_button(
        label="download as csv",
        data=counting_stats_csv,
        file_name=str(school) + "_counting_stats_" + str(season) + ".csv",
        mime="text/csv",
    )
    col3.write('')
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
        "2B-A",
        "3B-A",
        "GO",
        "FO",
        "W",
        "L",
        "SV",
    ]
    st.dataframe(counting_stats.style.format({"IP": "{:.1f}"}), width=1000)
    metrics1 = {
        "K/PA": "#2f4b7c",
        "BB/PA": "#2f4b7c",
        "BABIP-against": "#003f5c",
        "OBP-against": "#d45087",
        "SLG-against": "#f95d6a",
        "BA-against": "#ff7c43",
        "HR-A/PA": "#ffa600",
    }
    st.plotly_chart(
        create_dotplot(all_stats, school, season, metrics1),
        use_container_width=True,
    )
    st.write("")
    metrics2 = {"FIP": "darkorange", "ERA": "dodgerblue", "WHIP": "navy"}
    st.plotly_chart(
        create_dotplot(all_stats, school, season, metrics2),
        use_container_width=True,
    )
    st.write("")
    st.plotly_chart(
        create_scatter(all_stats, "ERA", "FIP", "BF", "Yr", school, season),
        use_container_width=True,
    )
    st.write("")
st.write("")
st.info(
    "Data from stats.ncaa.org. Percentiles relative to all D1 players with 20+ PA. Linear Weights courtesy of Robert Frey"
)
