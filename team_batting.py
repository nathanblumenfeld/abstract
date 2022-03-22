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

def create_histogram_new(data, metric, school, season):
    fig = px.histogram(data, x=metric, color='pos', marginal="rug", nbins=50, hover_name="name", template="seaborn", color_discrete_sequence= px.colors.qualitative.T10)
    fig.update_layout(title = str(school)+' Season '+metric+'s, '+str(season),
        title_yanchor = "top",
        title_x =  0.5,
        xaxis_title=metric,
        yaxis_title='')
    return fig 

def create_dotplot(df, school, season):
    """
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['BB%'],
        y=df['name'],
        marker=dict(color="lightblue", size=12),
        mode="markers",
        name="BB%",
    ))

    fig.add_trace(go.Scatter(
        x=df['K%'],
        y=df['name'],
        marker=dict(color="indianred", size=12),
        mode="markers",
        name="K%",
    ))
    fig.add_trace(go.Scatter(
        x=df['BA'],
        y=df['name'],
        marker=dict(color="crimson", size=12),
        mode="markers",
        name="BA",
    ))
    fig.add_trace(go.Scatter(
        x=df['OBP'],
        y=df['name'],
        marker=dict(color="darkorchid", size=12),
        mode="markers",
        name="OBP",
    ))
    fig.add_trace(go.Scatter(
        x=df['SLG'],
        y=df['name'],
        marker=dict(color="darkorange", size=12),
        mode="markers",
        name="SLG",
    ))
    fig.add_trace(go.Scatter(
        x=df['BABIP'],
        y=df['name'],
        marker=dict(color="lightpink", size=12),
        mode="markers",
        name="BABIP",
    ))
    fig.add_trace(go.Scatter(
        x=df['ISO'],
        y=df['name'],
        marker=dict(color="tan", size=12),
        mode="markers",
        name="ISO",
    ))
    
    fig.add_trace(go.Scatter(
        x=df['wOBA'],
        y=df['name'],
        marker=dict(color="yellow", size=12),
        mode="markers",
        name="wOBA",
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
                rate_stats = all_stats[['name', 'Yr', 'pos', 'PA', 'wOBA', 'OPS', 'K%', 'BB%', 'SLG', 'OBP', 'BA', 'BABIP', 'ISO']]
                counting_stats = all_stats[['name', 'Yr', 'pos', 'GP', 'PA', 'AB', 'H', '1B', '2B', '3B', 'HR', 'BB', 'IBB', 'HBP', 'RBI', 'R', 'SF', 'SH', 'K']]
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('### Rate Stats')
                rate_stats_csv = convert_df(rate_stats)
                col2.write('')
                col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(
                    school)+'_rate_stats_'+str(season)+'.csv', mime='text/csv')
                col3.write('')
                st.dataframe(rate_stats)
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('### Counting Stats')
                counting_stats_csv = convert_df(counting_stats)
                col2.write('')
                col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(
                    school)+'_counting_stats_'+str(season)+'.csv', mime='text/csv')
                col3.write('')
                st.dataframe(counting_stats)
                st.write('')
                st.plotly_chart(create_dotplot(all_stats, school, season), use_container_width=True)
                st.write('')
                st.plotly_chart(create_histogram_new(all_stats, 'wOBA', school, season), use_container_width=True)
            except: 
                st.warning('no records found')
            st.write('')          
            st.info('Data from stats.ncaa.org, valid 2013-2022. Linear Weights for seasons 2013-2021 courtesy of Robert Frey. Note: Linear Weights for 2022 season are average of past five seasons.')
