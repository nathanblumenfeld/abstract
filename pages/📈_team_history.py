from collegebaseball import win_pct
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from supabase import create_client
from st_aggrid import AgGrid

favicon = Image.open("assets/abstract_square_300dpi.png")

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=favicon,
    page_title="abstract",
)
st.sidebar.image(Image.open("assets/abstract_05x.png"))


@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = init_connection()

def load_games(school):
    rows = supabase.table("d1_games").select("*").eq('school', school).execute()
    df = pd.DataFrame(rows.data)
    return df

# def load_gamelogs(school, season):
#     df = ncaa.ncaa_team_game_logs(school, season, 'batting')
#     return df

def filter_games(school, seasons):
    df = load_games(school)
    df['season'] = df['season'].astype('int')
    res = df.loc[df.season.isin(seasons)]
    return res


def create_sparklines(df, school, start, end):
    """ """
    res = pd.DataFrame()
    for season in df.season.unique():
        new = df.loc[df.season == season].reset_index()
        new = new.drop(columns=["index"])
        new = new.reset_index()
        new.loc[:, "cumsum_rd"] = new["run_difference"].cumsum()
        new.loc[:, "game_number"] = new["index"]
        new = new.iloc[:, 2:]
        res = pd.concat([res, new])

    fig = px.line(
        res,
        x="game_number",
        y="cumsum_rd",
        color="season",
        color_discrete_sequence=[
            "#2f4b7c",
            "#ffa600",
            "#003f5c",
            "#a05195",
            "#d45087",
            "#f95d6a",
            "#ff7c43",
            "#2f4b7c",
            "#004c6d",
            "#255e7e",
            "#3d708f",
            "#5383a1",
            "#6996b3",
            "#7faac6",
            "#94bed9",
            "#c1e7ff",
        ],
        line_group="season",
    )
    fig.update_layout(
        title="Cumulative Run Differential by Season, "+school+" "+str(start)+"-"+str(end),
        title_font_size=20,
        title_xanchor="center",
        title_yanchor="top",
        title_x=0.5,
        yaxis_title="Cumulative Run Differential",
        xaxis_title="Games Played",
        margin=dict(l=40, r=20, t=60, b=20),
    )
    fig.update_yaxes(
        range=[min(-25, res.cumsum_rd.min() - 10), max(25, res.cumsum_rd.max() + 10)]
    )
    fig.update_yaxes(ticklabelposition="inside top")
    fig.update_yaxes(
        zeroline=True,
        zerolinewidth=5,
        zerolinecolor="coral",
        showgrid=True,
        gridwidth=0.75,
    )
    fig.update_xaxes(
        zeroline=True,
        zerolinewidth=2.5,
        zerolinecolor="darkslategray",
        showgrid=True,
        gridwidth=0.75,
    )
    fig.update_layout(showlegend=True)
    return fig


def load_school_lookup():
    return pd.read_parquet("data/valid_team_seasons.parquet")

@st.cache(persist=True, ttl=60 * 5)
def load_school_options():
    rows = supabase.table("schools").select("*").eq("division", 1).execute()
    df = pd.DataFrame(rows.data)
    df = df.loc[df.ncaa_name.notnull()]
    res = df.ncaa_name.unique()
    return res


school_options = load_school_options()
school_lookup = load_school_lookup()

school = st.selectbox("School", options=school_options, index=55, key="school_select")
with st.form(key="history_input"):
    col2, col3, col4, col5 = st.columns([0.5, 2, 0.5, 0.5])
    school_row = school_lookup.loc[school_lookup.school == school]
    valid_seasons = list(school_row.seasons_list.values[0]).copy()
    valid_seasons = [int(x) for x in valid_seasons]
    valid_seasons.sort()
    min_season = int(school_row["first_season"].values[0])
    max_season = int(school_row["last_season"].values[0])
    col2.markdown("#")
    start, end = col3.select_slider(
        "Seasons",
        options=valid_seasons,
        value=(min_season, max_season),
        key="seasons_slider",
    )
    season_input = [x for x in valid_seasons if ((x >= start) and (x <= end))]
    col4.markdown("#")
    col5.markdown("#")
    is_submitted = col5.form_submit_button("submit")

if is_submitted:
    games = filter_games(school, season_input)
    actual, wins, ties, losses = win_pct.calculate_actual_win_pct(games)
    expected, total_run_difference = win_pct.calculate_pythagenpat_win_pct(games)
    col1, col2, col3, col4, col5, col6 = st.columns([0.5, 1, 1, 1, 1, 0.1])
    with col1:
        st.write("")
    with col2:
        st.metric(
            label="Record",
            value=str(wins) + "-" + str(losses) + "-" + str(ties),
        )
    with col3:
        st.metric(label="Run Differential", value=str(total_run_difference))
    with col4:
        st.metric(label="Winning %: ", value=str(actual))
    with col5:
        st.metric(label="PythagenPat Expected Winning %: ", value=str(expected))
    with col6:
        st.write("")
    
    col1, col2, col3 = st.columns([0.5, 5, 0.5])
    with col1:
        st.write("")
    with col2:
        st.plotly_chart(create_sparklines(games, school, start, end), use_container_width=True)
    with col3:
        st.write("")

    col1, col2, col3 = st.columns([2, 5, 2])
    with col1:
        st.write("")
    with col2:
        games_display = games[
            [
                "date",
                "opponent",
                "runs_scored",
                "runs_allowed",
                "run_difference",
                "season",
            ]
        ]
        AgGrid(games_display)
    with col3:
        st.write("")



    st.write("")
    st.info("Data from boydsworld.com")
