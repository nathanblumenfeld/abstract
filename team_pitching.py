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
                       color_discrete_sequence= px.colors.qualitative.T10)
    fig.update_layout(title = str(school)+' Season '+metric+'s, '+str(season),
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
            name=i,
        ))                
    fig.update_layout(title=str(school)+" Pitchers, "+str(season), xaxis=dict(showgrid=False, showline=True, zerolinecolor='DarkSlateGrey'), yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='DarkSlateGrey'), height=len(df.name.unique())*35)
    # fig.update_xaxes(range=[0,1])
    return fig


def create_scatter(data, metric1, metric2, school, season):
    fig = px.scatter(data, x=metric1, y=metric2, hover_name="name")
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
            # all_stats = metrics.add_pitching_metrics(raw_stats)
            stats = ncaa.get_team_stats(school, season, 'pitching')
            all_stats = metrics.add_pitching_metrics(stats)
            rate_stats = all_stats[['name', 'Yr', 'IP', 'BF', 'ERA', 'FIP', 'WHIP', 'K/PA', 'BB/PA', 'OBP-against', 'BA-against', 'SLG-against', 'OPS-against', 'BABIP-against', 'Pitches/PA', 'HR-A/PA', 'IP/App']]
            counting_stats = all_stats[['name', 'Yr', 'IP', 'BF', 'App', 'H', 'SO', 'BB', 'ER', 'R', 'HR-A', 'HB', '2B-A', '3B-A', 'GO', 'FO', 'W', 'L', 'SV']]
            col1, col2, col3= st.columns([3,2,10])
            col1.markdown('### Rate Stats')
            rate_stats_csv = convert_df(rate_stats)
            col2.write('')
            col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(school)+'_rate_stats_'+str(season)+'.csv', mime='text/csv')
            col3.write('')
            st.dataframe(rate_stats)
            st.write('')
            col1, col2, col3 = st.columns([3,2,10])
            col1.markdown('### Counting Stats')
            counting_stats_csv = convert_df(counting_stats)
            col2.write('')
            col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(school)+'_counting_stats_'+str(season)+'.csv', mime='text/csv')
            col3.write('')
            st.dataframe(counting_stats)
            metrics1 = {'K/PA':'indianred', 'BB/PA':'dodgerblue', 
               'BABIP-against':'crimson', 'BABIP-against':'darkorchid',
               'OBP-against':'darkorange', 'SLG-against':'darkblue',
               'BA-against':'forestgreen', 'HR-A/PA':'tan'}
            st.plotly_chart(create_dotplot(all_stats, school, season, metrics1), use_container_width=True)
            st.write('')
            metrics2 = {'FIP':'darkorange', 'ERA':'dodgerblue', 'WHIP':'navy'}
            st.plotly_chart(create_dotplot(all_stats, school, season, metrics2), use_container_width=True)
            st.write('')
            st.plotly_chart(create_scatter(all_stats, 'BF', 'FIP', school, season), use_container_width=True)
            st.write('')
            st.plotly_chart(create_histogram(all_stats, 'OBP-against', school, season, 'Yr'), use_container_width=True)
            st.write('')          