from collegebaseball import metrics
from collegebaseball import win_pct
from collegebaseball import ncaa_scraper as ncaa
from collegebaseball import boydsworld_scraper as bd
import streamlit as st

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

from hydralit import HydraHeadApp

@st.cache(persist=True)
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

def load_player_lookup(): 
    return pd.read_parquet('collegebaseball/data/players_history.parquet')

def load_season_stats(season, variant, positions, schools, minimum, class_years): 
    """
    """
    df = pd.read_parquet('collegebaseball/data/'+variant+'_stats_all_'+str(season)+'_position.parquet')
    res = df 
    if schools:
        if not 'all' in schools: 
            res =  df.loc[df.school.isin(schools)]

    if positions:
        if 'all' not in positions:
            res = res.loc[res.position.isin(positions)]
        
    if minimum > 0: 
        if variant == 'batting': 
            res = res.loc[res.PA >= minimum]
        else: 
            res = res.loc[res['IP'] >= minimum]
        
    if class_years: 
        if 'all' not in class_years: 
            if 'other' in class_years:
                class_years.remove('other')
                class_years.append('N/A')
            res = res.loc[res.Yr.isin(class_years)]
        
    if variant == 'batting':
        res = res[['name', 'Yr', 'school', 'position', 'PA', 'H', '2B', '3B', 'HR', 'RBI', 'R', 'BB', 'IBB', 'HBP', 'SF', 'SH', 'K', 'GP', 'AB', '1B', 'wOBA', 'OPS', 'OBP', 'SLG', 'BA', 'ISO', 'BABIP', 'HR%', 'K%', 'BB%', 'wRAA', 'wRC']]
    else: 
        res = res[['name', 'Yr', 'school', 'position', 'BF', 'IP', 'FIP', 'ERA', 'WHIP', 'SO', 'BB', 'H', 'HR-A', 'ER', 'R', 'OPS-against', 'OBP-against', 'SLG-against', 'BA-against', 'K/PA', 'K/9', 'BB/PA', 'BB/9', 'HR-A/PA']]
    return res

def _calculate_percentiles(df, variant): 
    """
    """
    if variant == 'batting': 
        stats = ['OBP', 'BA', 'SLG', 'OPS', 'ISO', 'HR%', 'K%', 'BB%', 'BABIP', 'wOBA', 'wRAA', 'wRC']
    else: 
        stats = ['ERA', 'IP', 'BF', 'OBP-against', 'BA-against', 'SLG-against', 'OPS-against', 'K/PA', 'K/9', 'BB/PA', 'BB/9', 'FIP', 'WHIP', 'HR-A/PA']

    for stat in stats: 
        df[stat+'-percentile'] = pd.qcut(df[stat], q=100, labels=False, duplicates='drop')
    return df

def load_player_options(): 
    df = load_player_lookup()
    df.set_index("stats_player_seq", drop=True, inplace=True)
    dictionary = df.to_dict(orient="index")
    return dictionary

def load_school_lookup(): 
    return pd.read_parquet('collegebaseball/data/team_seasons.parquet')

def load_school_options(): 
    df = load_school_lookup()
    options = list(df.school.unique())
    options.insert(0, 'all')
    return options

# show dist

class LeaderboardsApp(HydraHeadApp):
    def run(self): 
        # with st.form(key="leaderboards_input"):
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        season = col1.selectbox('Season', options=range(2013, 2023), index=9, key='season_select')
        stats_type = col5.selectbox('Stats Type', options=['batting', 'pitching'], index=0, key='stats_type_select')
        class_years = col4.multiselect('Class Year', options=['all', 'Fr', 'So', 'Jr', 'Sr', 'other'], default='all', key='stats_type_select')
        if stats_type == 'batting':
            positions = col3.multiselect('Position', options=['all', 'INF', 'OF', 'C', 'P', 'DH'], default='all', key='position_select') 
            minimum = col6.number_input('Min. PA', min_value=0, value=20, step=1)
        else: 
            position = col3.selectbox('Position', options=['all', 'P', 'notP'], index=0, key='position_select')
            minimum = col6.number_input('Min. IP', min_value=0, value=10, step=1)

        schools = col2.multiselect('School', options=load_school_options(), default='all', key='school_select')
        # submitted = col5.form_submit_button('submit')
        stats = load_season_stats(season, stats_type, positions, schools, minimum, class_years)
        hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
        """
        if stats_type == 'batting':
            # top_5 = 

            counting_stats = stats[['name', 'Yr', 'school', 'position', 'PA', 'H', '2B', '3B', 'HR', 'K', 'BB', 'R', 'RBI', 'IBB', 'SF', 'SH', 'HBP']]
            counting_slice = ['PA', 'H', '2B', '3B', 'HR', 'BB', 'K', 'IBB', 'HBP', 'RBI', 'R', 'SF', 'SH']
            rate_stats = stats[['name', 'Yr', 'school', 'position', 'PA', 'wOBA', 'wRC', 'wRAA', 'OPS', 'OBP', 'SLG', 'BA', 'ISO', 'BABIP', 'K%', 'BB%', 'HR%']]
            rate_slice = ['PA', 'wOBA', 'wRC', 'wRAA', 'OPS', 'OBP', 'SLG', 'BA', 'BABIP', 'ISO', 'K%', 'BB%', 'HR%']
            
            col1, col2, col3= st.columns([3,2,10])
            col1.markdown('## Counting Stats')
            counting_stats_csv = convert_df(counting_stats)
            col2.markdown('#')
            col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(season)+'_'+stats_type+'_counting_stat_leaders'+'_'+str(positions)+'_'+str(schools)+'_minPA_'+str(minimum)+'.csv', mime='text/csv')
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
            st.dataframe(counting_stats.style.highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=counting_slice))

            col1, col2, col3= st.columns([3,2,10])
            col1.markdown('## Rate Stats')
            rate_stats_csv = convert_df(rate_stats)
            col2.markdown('#')
            col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(season)+'_'+stats_type+'_rate_stat_leaders'+'_'+str(positions)+'_'+str(schools)+'_minPA_'+str(minimum)+'.csv', mime='text/csv')

            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
            st.dataframe(rate_stats.style.format({"PA": '{:.0f}', "wOBA": '{:.3f}', "wRC": '{:.1f}', "wRAA": '{:.1f}', "OPS": '{:.3f}', "OBP": '{:.3f}', "SLG": '{:.3f}', "BA": '{:.3f}', "BABIP": '{:.3f}', "ISO": '{:.3f}', "K%": '{:,.2%}', "BB%": '{:,.2%}', "HR%": '{:,.2%}'}, na_rep="", subset=rate_slice).highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=rate_slice))
#         else: 
            
#             counting_stats = stats[['name', 'Yr', 'school', 'position', 'PA', 'H', '2B', '3B', 'HR', 'K', 'BB', ]]
#             rate_stats = stats[['']]
#             st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
#             st.dataframe(counting_stats)

        st.write('')          
        st.info('Data from stats.ncaa.org, valid 2013-2022. Linear Weights for seasons 2013-2021 courtesy of Robert Frey. Note: Linear Weights for 2022 season are average of past five seasons.')
