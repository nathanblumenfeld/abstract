"""
A college baseball team history page implemented as a subclass of HydraHeadApp
Displays data from BoydsWorld.com using boydsworld_scraper

Nathan Blumenfeld
2022
"""
from collegebaseball import win_pct

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from hydralit import HydraHeadApp

@st.cache()
def load_games(): 
    df = pd.read_parquet('collegebaseball/data/games_all_1992_2021.parquet')
    return df

@st.cache()
def load_results(variant, season): 
    df = pd.read_parquet('collegebaseball/data/team_gbg_all_'+variant+'_'+season+'.parquet')
    return df 

def filter_games(school, seasons):
    df = load_games()
    res = df.loc[(df.school == school) & (df.season.isin(seasons))]
    res = res.reset_index().iloc[:, 1:]
    res.loc[:, 'date'] = res.date.dt.date
    return res 

def create_sparklines(df):
    """
    """
    res = pd.DataFrame()
    for season in df.season.unique():
        new = df.loc[df.season == season].reset_index()
        new = new.drop(columns=['index'])
        new = new.reset_index()
        new.loc[:, 'cumsum_rd'] = new['run_difference'].cumsum()
        new.loc[:, 'game_number'] = new['index']
        new = new.iloc[:,2:]
        res = pd.concat([res, new])
        
    fig = px.line(res, x="game_number", y="cumsum_rd", color='season', 
    color_discrete_sequence=['#2f4b7c', '#ffa600', '#003f5c', '#a05195', '#d45087', '#f95d6a',
                            '#ff7c43', '#2f4b7c', '#004c6d', '#255e7e', '#3d708f', '#5383a1', 
                            '#6996b3', '#7faac6', '#94bed9', '#c1e7ff'], line_group='season')
    fig.update_layout( 
        title = f"""Cumulative Run Differential by Season""",
        title_font_size = 20,
        title_xanchor = "center",
        title_yanchor = "top",
        title_x =  0.5,
        yaxis_title="Cumulative Run Differential",
        xaxis_title="Games Played",
        margin=dict(l=40, r=20, t=60, b=20)
    )
    fig.update_yaxes(range=[min(-25, res.cumsum_rd.min()-10), max(25, res.cumsum_rd.max()+10)])
    fig.update_yaxes(ticklabelposition="inside top")
    fig.update_yaxes(zeroline=True, zerolinewidth=5, zerolinecolor='coral', showgrid=True, gridwidth=0.75)
    fig.update_xaxes(zeroline=True, zerolinewidth=2.5, zerolinecolor='darkslategray', showgrid=True, gridwidth=0.75)
    fig.update_layout(showlegend=True)
    return fig

    
def load_school_lookup(): 
    return pd.read_parquet('collegebaseball/data/team_seasons.parquet')

def load_school_options(): 
    df = pd.read_parquet('collegebaseball/data/schools.parquet')
    df = df.loc[df.bd_name.notnull()]
    options = df.bd_name.unique()
    
    return options

class TeamHistoryApp(HydraHeadApp):
    def run(self): 
        school_options = load_school_options()
        school_lookup = load_school_lookup()
        
        school = st.selectbox('School', options=school_options, index=55, key='school_select')
        with st.form(key="history_input"):
            col2, col3, col4, col5 = st.columns([.5, 2,.5, .5])
            school_row = school_lookup.loc[school_lookup.school == school]
            valid_seasons = list(school_row.seasons.values[0]).copy()
            valid_seasons.sort()
            min_season = school_row['first'].values[0]
            max_season = school_row['last'].values[0]
            col2.markdown('#')
            start, end = col3.select_slider('Seasons', options=valid_seasons, value=(min_season, max_season), key='seasons_slider')
            season_input = [x for x in valid_seasons if ((x >= start) and (x <= end))]
            col4.markdown('#')
            col5.markdown('#')
            is_submitted = col5.form_submit_button('submit')

        if is_submitted: 
            # try: 
            games = filter_games(school, season_input)
            actuals = win_pct.calculate_actual_win_pct(school, games = games)
            expecteds = win_pct.calculate_pythagenpat_win_pct(school, games = games)
            col1, col2, col3, col4, col5, col6 = st.columns([.5, 1, 1, 1, 1, .1])
            with col1: 
                st.write('')
            with col2: 
                st.metric(label="Record", value=str(actuals[1])+'-'+str(actuals[3])+'-'+str(actuals[2]))
            with col3: 
                st.metric(label="Run Differential", value=str(expecteds[1]))
            with col4: 
                st.metric(label="Winning %: ", value=str(actuals[0]))
            with col5: 
                st.metric(label="PythagenPat Expected Winning %: ", value=str(expecteds[0]))
            with col6: 
                st.write('')
                
            hide_dataframe_row_index = """
                    <style>
                    .row_heading.level0 {display:none}
                    .blank {display:none}
                    </style>
                    """
            col1, col2, col3 = st.columns([2, 5, 2])
            with col1: 
                st.write('')
            with col2: 
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                games_display = games[['date', 'opponent', 'runs_scored', 'runs_allowed', 'run_difference', 'season']]
                st.dataframe(games_display.style.bar(align = 'mid', subset=['run_difference', 'runs_scored', 'runs_allowed'], color=['#C05353', '#67A280']))
            with col3: 
                st.write('')
                
            col1, col2, col3 = st.columns([.5, 5, .5])
            with col1: 
                st.write('')
            with col2: 
                st.plotly_chart(create_sparklines(games), use_container_width=True)
            with col3: 
                st.write('')
                # except: 
                #     st.warning('no records found')
            st.write('')
            st.info('Data from boydsworld.com, valid 1992-2021.')
