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

def create_histogram(data, metric, school, season, color):
    fig = px.histogram(data, x=metric, color=color, marginal="rug", nbins=50,
                       hover_name="name", template="seaborn",
                       color_discrete_sequence=['#003f5c', '#7a5195', '#ef5675', '#ffa600'])
    fig.update_layout(title = str(school)+' Season '+metric+'s, '+str(season), title_yanchor = "top",
        title_x =  0.5, xaxis_title=metric, yaxis_title='')
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
    fig.update_layout(title=str(school)+" Pitchers, "+str(season), xaxis=dict(showgrid=False, showline=True, zerolinecolor='DarkSlateGrey'), yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='DarkSlateGrey'), height=len(df.name.unique())*35)
    return fig


def create_scatter(data, metric1, metric2, metric3, metric4, school, season):
    fig = px.scatter(data, x=metric1, y=metric2, hover_name="name", size=metric3, color=metric4, color_discrete_sequence=['#003f5c', '#7a5195', '#ef5675', '#ffa600'])
    fig.update_layout(
        title = str(school)+' '+str(season)+', '+str(metric2)+' vs '+str(metric1),
        title_yanchor = "top",
        title_x = 0.5,
        xaxis_title=str(metric1),
        yaxis_title=str(metric2)
    )
    return fig


class TeamPitchingApp(HydraHeadApp):
    def run(self): 
        school_options = load_school_options()
        with st.form('team_pitching'):
            col1, col2, col3, col4 = st.columns([3,.25,2,2])
            school = col1.selectbox('School', options=school_options, index=55, key='team_pitching_school')
            col2.write('')
            season = col3.number_input('Season', min_value=2012, max_value=2022, value=2022, key='team_pitching_season')
            col4.markdown('#')
            team_pitching_submit = col4.form_submit_button('submit')

        if team_pitching_submit:
            try: 
                stats = ncaa.get_team_stats(school, season, 'pitching')
                all_stats = metrics.add_pitching_metrics(stats)
                rate_stats = all_stats[['name', 'Yr', 'IP', 'BF', 'ERA', 'FIP', 'WHIP', 'K/PA', 'BB/PA', 'OPS-against', 'OBP-against', 'SLG-against', 'BA-against', 'BABIP-against', 'Pitches/PA', 'HR-A/PA', 'IP/App']]
                counting_stats = all_stats[['name', 'Yr', 'IP', 'BF', 'App', 'H', 'SO', 'BB', 'ER', 'R', 'HR-A', 'HB', '2B-A', '3B-A', 'GO', 'FO', 'W', 'L', 'SV']]
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('## Rate Stats')
                rate_stats_csv = convert_df(rate_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(school)+'_rate_stats_'+str(season)+'.csv', mime='text/csv')
                hide_dataframe_row_index = """
                        <style>
                        .row_heading.level0 {display:none}
                        .blank {display:none}
                        </style>
                """
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                rate_slice = ['IP', 'BF', 'ERA', 'FIP', 'WHIP', 'K/PA', 'BB/PA', 'OPS-against', 'OBP-against', 'SLG-against', 'BA-against', 'BABIP-against', 'Pitches/PA', 'HR-A/PA', 'IP/App']
                st.dataframe(rate_stats.style.format({"IP": '{:.0f}', "BF": '{:.0f}', "ERA": '{:.3f}', "FIP": '{:.3f}', "WHIP": '{:.3f}', "K/PA": '{:.3f}', "BB/PA": '{:.3f}', "OPS-against": '{:.3f}', "OBP-against": '{:.3f}', "SLG-against": '{:.3f}', "BA-against": '{:.3f}', "Pitches/PA": '{:.3f}', "HR-A/PA": '{:.3f}', "IP/App": '{:.3f}'}, na_rep="", subset=rate_slice).highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=rate_slice).highlight_min(axis=0, props='color:white; font-weight:bold; background-color:#d45087;', subset=rate_slice))
                st.write('')
                col1, col2, col3 = st.columns([3,2,10])
                col1.markdown('## Counting Stats')
                counting_stats_csv = convert_df(counting_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(school)+'_counting_stats_'+str(season)+'.csv', mime='text/csv')
                counting_slice = ['IP', 'BF', 'App', 'H', 'SO', 'BB', 'ER', 'R', 'HR-A', 'HB', '2B-A', '3B-A', 'GO', 'FO', 'W', 'L', 'SV']
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                st.dataframe(counting_stats.style.highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=counting_slice).highlight_min(axis=0, props='color:white; font-weight:bold; background-color:#d45087;', subset=counting_slice))

                metrics1 = {'K/PA':'#2f4b7c', 'BB/PA':'#2f4b7c', 
                'BABIP-against':'#003f5c', 'BABIP-against':'#a05195',
                'OBP-against':'#d45087', 'SLG-against':'#f95d6a',
                'BA-against':'#ff7c43', 'HR-A/PA':'#ffa600'}
                st.plotly_chart(create_dotplot(all_stats, school, season, metrics1), use_container_width=True)
                st.write('')
                metrics2 = {'FIP':'darkorange', 'ERA':'dodgerblue', 'WHIP':'navy'}
                st.plotly_chart(create_dotplot(all_stats, school, season, metrics2), use_container_width=True)
                st.write('')
                st.plotly_chart(create_scatter(all_stats, 'ERA', 'FIP', 'BF', 'Yr', school, season), use_container_width=True)
                st.write('')
                st.plotly_chart(create_histogram(all_stats, 'OPS-against', school, season, 'Yr'), use_container_width=True)
            except: 
                st.warning('no records found')
            st.write('')          
            st.info('Data from stats.ncaa.org. Linear Weights for seasons 2013-2021 courtesy of Robert Frey. Note: Linear Weights for 2022 season are average of past five seasons.')
