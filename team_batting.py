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


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

    
def load_school_lookup(): 
    return pd.read_parquet('collegebaseball/data/team_seasons.parquet')

def load_school_options(): 
    df = load_school_lookup()
    options = df.school.unique()
    return options

def create_histogram(data, metric, school, season):
    fig = px.histogram(data, x=metric, color='pos', marginal="rug", nbins=50, hover_name="name", template="seaborn", color_discrete_sequence=['#003f5c', '#7a5195', '#ef5675', '#ffa600'])
    fig.update_layout(title = str(school)+' single-season '+metric+"'s, "+str(season),
        title_yanchor = "top",
        title_x =  0.5,
        xaxis_title=metric,
        yaxis_title='')
    return fig 

def create_dotplot(df, school, season, metrics):
    """
    """
    fig = go.Figure()
    for i in metrics.keys():
        fig.add_trace(go.Scatter(
                x=df[i],
                y=df['name'],
                marker=dict(color=metrics[i], size=12),
                mode="markers",
                name=i
        ))      
    fig.update_layout(title=str(school)+" batters, "+str(season), xaxis=dict(showgrid=False, showline=True, zerolinecolor='DarkSlateGrey'), yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='DarkSlateGrey'), height=len(df.name.unique())*35)
    fig.update_xaxes(range=[0,1])
    return fig

class TeamBattingApp(HydraHeadApp):
    def run(self): 
        school_options = load_school_options()
        with st.form('team_batting'):
            col1, col2, col3, col4 = st.columns([3,.25,2,2])
            school = col1.selectbox('School', options=school_options, index=55, key='team_batting_school')
            col2.write('')
            season = col3.number_input('Season', min_value=2012, max_value=2022, value=2022, key='team_batting_season')
            col4.markdown('#')
            team_batting_submit = col4.form_submit_button('submit')

        if team_batting_submit:
            try: 
                raw_stats = ncaa.get_team_stats(school, season, 'batting')
                all_stats = metrics.add_batting_metrics(raw_stats)
                rate_stats = all_stats[['name', 'Yr', 'pos', 'GP', 'PA', 'wOBA', 'OPS', 'OBP', 'SLG', 'BA', 'BABIP', 'ISO', 'K%', 'BB%', 'HR%']]
                counting_stats = all_stats[['name', 'Yr', 'pos', 'GP', 'PA', 'AB', 'H', '1B', '2B', '3B', 'HR', 'BB', 'K', 'IBB', 'HBP', 'RBI', 'R', 'SF', 'SH']]
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('## Rate Stats')
                rate_stats_csv = convert_df(rate_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(
                    school)+'_rate_stats_'+str(season)+'.csv', mime='text/csv')
                rate_slice = ['GP', 'PA', 'wOBA', 'OPS', 'OBP', 'SLG', 'BA', 'BABIP', 'ISO', 'K%', 'BB%', 'HR%']
                hide_dataframe_row_index = """
                        <style>
                        .row_heading.level0 {display:none}
                        .blank {display:none}
                        </style>
                """
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                st.dataframe(rate_stats.style.format({"PA": '{:.0f}', "wOBA": '{:.3f}', "OPS": '{:.3f}', "OBP": '{:.3f}', "SLG": '{:.3f}', "BA": '{:.3f}', "BABIP": '{:.3f}', "ISO": '{:.3f}', "K%": '{:,.2%}', "BB%": '{:,.2%}', "HR%": '{:,.2%}'}, na_rep="", subset=rate_slice).highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=rate_slice).highlight_min(axis=0, props='color:white; font-weight:bold; background-color:#d45087;', subset=rate_slice))
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('## Counting Stats')
                counting_stats_csv = convert_df(counting_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(
                    school)+'_counting_stats_'+str(season)+'.csv', mime='text/csv')
                counting_slice = ['PA', 'GP', 'AB', 'H', '1B', '2B', '3B', 'HR', 'BB', 'K', 'IBB', 'HBP', 'RBI', 'R', 'SF', 'SH']
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                st.dataframe(counting_stats.style.highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=counting_slice).highlight_min(axis=0, props='color:white; font-weight:bold; background-color:#d45087;', subset=counting_slice))
                st.write('')
                rate_metrics = {'BB%':'#003f5c', 'K%':'#2f4b7c', 'BA':'#665191', 'OBP':'#d45087', 'wOBA':'#f95d6a', 'BABIP':'#ff7c43', 'SLG':'#ffa600'}
                st.plotly_chart(create_dotplot(all_stats, school, season, rate_metrics), use_container_width=True)
                st.write('')
                st.plotly_chart(create_histogram(all_stats, 'wOBA', school, season), use_container_width=True)
            except: 
                st.warning('no records found')
            st.write('')          
            st.info('Data from stats.ncaa.org, valid 2013-2022. Linear Weights for seasons 2013-2021 courtesy of Robert Frey. Note: Linear Weights for 2022 season are average of past five seasons.')
