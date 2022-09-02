from collegebaseball import metrics
from collegebaseball import ncaa_scraper as ncaa
from PIL import Image
from supabase import create_client

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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


@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = init_connection()


def load_player_lookup():
    rows = supabase.table("d1_player_lookup").select("*").execute()
    res = pd.DataFrame(rows.data)
    res = res.set_index('stats_player_seq')
    res = res.sort_values(by='season', ascending=False)
    return res


def create_scatter(data, metric1, metric2, metric3, player):
    data = data.sort_values(by="season", ascending=False)
    data.season = data.season.astype("str")
    fig = px.scatter(
        data,
        x=metric1,
        y=metric2,
        size=metric3,
        color="season",
        template="seaborn",
        color_discrete_sequence=["#003f5c", "#7a5195", "#ef5675", "#ffa600"],
    )
    fig.update_layout(
        title=str(player)
        + ", "
        + str(metric2)
        + " vs "
        + str(metric1)
        + " by season <br><sub>size = PA</sub>",
        xaxis_title=str(metric1),
        yaxis_title=str(metric2),
    )
    return fig


def create_histogram(data, metric, player):
    fig = px.histogram(
        data,
        x=metric,
        color="season",
        marginal="rug",
        nbins=50,
        template="none",
        color_discrete_sequence=["#003f5c", "#7a5195", "#ef5675", "#ffa600"],
    )
    fig.update_layout(
        title=str(player) + " career " + metric,
        title_yanchor="top",
        title_x=0.5,
        xaxis_title=metric,
        yaxis_title="",
    )
    return fig


def create_dotplot(df, player, metrics):
    """ """
    df = df.sort_values(by="season", ascending=True)
    fig = go.Figure()
    for i in metrics.keys():
        fig.add_trace(
            go.Scatter(
                x=df[i],
                y=df["season"],
                marker=dict(color=metrics[i], size=12),
                mode="lines+markers",
                name=i,
            )
        )
        fig.update_layout(
            title=str(player) + ", career progression",
            xaxis=dict(showgrid=False, showline=False),
            yaxis=dict(showgrid=True, showline=False, gridwidth=0.5, tickmode="linear"),
            height=len(df.season.unique()) * 125 + 125,
        )
        fig.update_yaxes(tickvals=df["season"].unique(), autorange="reversed")
    return fig

player_options = load_player_lookup().to_dict('index')
with st.form("player_input"):
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    player_id = col1.selectbox(
        "Player",
        options=player_options.keys(),
        format_func=lambda x: str(player_options[x]["name"])
        + ", "
        + str(player_options[x]["position"])
        + ", "
        + str(player_options[x]["school"]),
        index=190,
        key="player_id_input",
    )
    player_name = player_options.get(int(player_id))["name"]
    col3.write("")
    variant = col2.selectbox(
        "Stats Type", options=["batting", "pitching"], key="team_stats_type"
    )
    col4.markdown("#")
    submitted = col4.form_submit_button("submit")

if submitted:
    stats = ncaa.ncaa_career_stats(int(player_id), variant)
    # try:
    if variant == "batting":
        rate_stats = stats[
            [
                "season",
                "PA",
                "wOBA",
                "OPS",
                "OBP",
                "SLG",
                "BA",
                "ISO",
                "K/PA",
                "BB/PA",
                "BABIP",
                "HR/PA",
            ]
        ]
        counting_stats = stats[
            [
                "season",
                "PA",
                "H",
                "1B",
                "2B",
                "3B",
                "HR",
                "BB",
                "IBB",
                "K",
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
        col2.markdown("#")
        col2.download_button(
            label="download as csv",
            data=rate_stats_csv,
            file_name=str(player_name) + "_career_rate_stats_.csv",
            mime="text/csv",
        )
        rate_slice = [
            "PA",
            "wOBA",
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
        st.dataframe(
            rate_stats.style.format(
                {
                    "PA": "{:.0f}",
                    "wOBA": "{:.3f}",
                    "OPS": "{:.3f}",
                    "OBP": "{:.3f}",
                    "SLG": "{:.3f}",
                    "BA": "{:.3f}",
                    "BABIP": "{:.3f}",
                    "ISO": "{:.3f}",
                    "K/PA": "{:,.2%}",
                    "BB/PA": "{:,.2%}",
                    "HR/PA": "{:,.2%}",
                },
                na_rep="",
                subset=rate_slice,
            )
        )
        st.markdown("#")
        col1, col2, col3 = st.columns([3, 2, 10])
        col1.markdown("## Counting Stats")
        counting_stats_csv = convert_df(counting_stats)
        col2.markdown("")
        col2.download_button(
            label="download as csv",
            data=counting_stats_csv,
            file_name=str(player_name) + "_career_counting_stats_.csv",
            mime="text/csv",
        )
        col3.write('')
        counting_slice = [
            "PA",
            "H",
            "1B",
            "2B",
            "3B",
            "HR",
            "BB",
            "IBB",
            "K",
            "HBP",
            "RBI",
            "R",
            "SF",
            "SH",
        ]
        st.dataframe(counting_stats)
        rate_metrics = {
            "BB/PA": "#003f5c",
            "K/PA": "#2f4b7c",
            "BA": "#665191",
            "OBP": "#d45087",
            "wOBA": "#f95d6a",
            "BABIP": "#ff7c43",
            "SLG": "#ffa600",
        }
        st.plotly_chart(
            create_dotplot(stats, player_name, rate_metrics),
            use_container_width=True,
        )
        st.write("")
        st.plotly_chart(
            create_scatter(stats, "OBP", "wOBA", "PA", player_name),
            use_container_width=True,
        )
        st.write("")
    else:
        all_stats = metrics.add_pitching_metrics(stats).sort_values(by="season")
        rate_stats = all_stats[
            [
                "season",
                "IP",
                "BF",
                "ERA",
                "FIP",
                "WHIP",
                "K/PA",
                "BB/PA",
                "OPS-against",
                "OBP-against",
                "BA-against",
                "SLG-against",
                "BABIP-against",
                "wOBA-against",
                "Pitches/PA",
                "HR-A/PA",
            ]
        ]
        counting_stats = all_stats[
            [
                "season",
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
            file_name=str(player_name) + "_career_rate_stats_.csv",
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
            "wOBA-against",
            "Pitches/PA",
            "HR-A/PA"
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
                    "wOBA-against": "{:.3f}",
                    "SLG-against": "{:.3f}",
                    "BA-against": "{:.3f}",
                    "Pitches/PA": "{:.3f}",
                    "HR-A/PA": "{:.3f}"
                },
                na_rep="",
                subset=rate_slice,
            )
        )
        st.write("")
        col1, col2, col3 = st.columns([3, 2, 10])
        col1.markdown("## Counting Stats")
        counting_stats_csv = convert_df(counting_stats)
        col2.markdown("")
        col2.download_button(
            label="download as csv",
            data=counting_stats_csv,
            file_name=str(player_name) + "_career_counting_stats_.csv",
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
        st.dataframe(counting_stats.style.format({"IP": "{:.1f}"}))
        metrics1 = {
            "K/PA": "#2f4b7c",
            "HR-A/PA": "#ffa600",
            "BABIP-against": "#003f5c",
            "wOBA-against": "#a05195",
            "OBP-against": "#d45087",
            "SLG-against": "#f95d6a",
            "BA-against": "#ff7c43",
            "BB/PA": "#2f4b7c",
        }
        st.plotly_chart(
            create_dotplot(all_stats, player_name, metrics1),
            use_container_width=True,
        )
        st.write("")
        metrics2 = {"FIP": "#2f4b7c", "ERA": "#d45087", "WHIP": "#ffa600"}
        st.plotly_chart(
            create_dotplot(all_stats, player_name, metrics2),
            use_container_width=True,
        )
        st.write("")
        st.plotly_chart(
            create_scatter(all_stats, "ERA", "FIP", "BF", player_name),
            use_container_width=True,
        )

st.write("")
st.info(
    "Data from stats.ncaa.org. Linear Weights courtesy of Robert Frey."
)
