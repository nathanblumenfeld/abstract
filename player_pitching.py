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

def load_player_lookup(): 
    return pd.read_parquet('collegebaseball/data/players_history_new_3.parquet')

def load_player_options(): 
    df = load_player_lookup()
    df.set_index("stats_player_seq", drop=True, inplace=True)
    dictionary = df.to_dict(orient="index")
    return dictionary

def create_histogram(data, metric, player):
    fig = px.histogram(data, x=metric, color='season', marginal="rug", nbins=50, template="none",
                       color_discrete_sequence= px.colors.qualitative.T10)
    fig.update_layout(title = str(player)+' career '+metric,
        title_yanchor = "top",
        title_x =  0.5,
        xaxis_title=metric,
        yaxis_title='')
    return fig 

def create_dotplot(df, player, metrics):
    """
    """
    df = df.sort_values(by='season', ascending=True)
    fig = go.Figure()
    for i in metrics.keys(): 
        if len(df.season.unique()) > 1:
            fig.add_trace(go.Scatter(
                x=df['season'],
                y=df[i],
                marker=dict(color=metrics[i], size=12),
                mode="lines+markers",
                name=i,
            ))                
            fig.update_layout(title=str(player)+' career stats', yaxis=dict(showgrid=True, showline=False), xaxis=dict(showgrid=True, showline=False, gridwidth=0.5, tickmode = 'linear'), height=(len(df.season.unique())*125)+125
            )
            fig.update_xaxes(
                tickvals=df['season'].unique()
            )
        else: 
            fig.add_trace(go.Scatter(
                x=df[i],
                y=df['season'],
                marker=dict(color=metrics[i], size=12),
                mode="lines+markers",
                name=i,
            ))                
            fig.update_layout(title=str(player)+' career stats', xaxis=dict(showgrid=True, showline=False), yaxis=dict(showgrid=True, showline=False, gridwidth=0.5, tickmode = 'linear'), height=(len(df.season.unique())*125)+125
            )
            fig.update_yaxes(
                tickvals=df['season'].unique()
            )
    return fig


def create_scatter(data, metric1, metric2, player):
    data = data.sort_values(by='season', ascending=False)
    data.season = data.season.astype('str')
    fig = px.scatter(data, x=metric1, y=metric2, color='season', template='seaborn', color_discrete_sequence= px.colors.qualitative.T10)
    fig.update_layout(
        title = str(player)+', '+str(metric2)+' vs '+str(metric1),
        title_yanchor = "top",
        title_x = 0.5,
        xaxis_title=str(metric1),
        yaxis_title=str(metric2)
    )
    fig.update_traces(marker_size=10)
    return fig


class PlayerPitchingApp(HydraHeadApp):
    def run(self): 
        player_options = load_player_options()
        with st.form('player_pitching'):
            col1, col2, col3 = st.columns([3,.25, 2])
            player_id = col1.selectbox('Player', options=player_options.keys(), 
                                    format_func=lambda x: str(player_options.get(x)['name'])+' | '+str(player_options.get(x)['position_set'])+' | '+str(player_options.get(x)['school_set']+' | '+str(player_options.get(x)['season_set'])), key='pitching_player')
            player_name = ncaa._format_names(player_options.get(player_id)['name'])
            col2.write('')
            col3.markdown('#')
            player_pitching_submit = col3.form_submit_button('submit')

        
        if player_pitching_submit:
            try: 
                stats = ncaa.get_career_stats(player_id, 'pitching')
                all_stats = metrics.add_pitching_metrics(stats).sort_values(by='season')
                rate_stats = all_stats[['season', 'IP', 'BF', 'ERA', 'FIP', 'WHIP', 'K/PA', 'BB/PA', 'OBP-against', 'BA-against', 'SLG-against', 'OPS-against', 'BABIP-against', 'Pitches/PA', 'HR-A/PA', 'IP/App']]
                counting_stats = all_stats[['season', 'IP', 'BF', 'App', 'H', 'SO', 'BB', 'ER', 'R', 'HR-A', 'HB', '2B-A', '3B-A', 'GO', 'FO', 'W', 'L', 'SV']]
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('### Rate Stats')
                rate_stats_csv = convert_df(rate_stats)
                col2.write('')
                col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(player_name)+'_career_rate_stats_.csv', mime='text/csv')
                col3.write('')
                st.dataframe(rate_stats)
                st.write('')
                col1, col2, col3 = st.columns([3,2,10])
                col1.markdown('### Counting Stats')
                counting_stats_csv = convert_df(counting_stats)
                col2.write('')
                col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(player_name)+'_career_counting_stats_.csv', mime='text/csv')
                col3.write('')
                st.dataframe(counting_stats)
                metrics1 = {'K/PA':'indianred', 'BB/PA':'dodgerblue', 
                   'BABIP-against':'crimson', 'BABIP-against':'darkorchid',
                   'OBP-against':'darkorange', 'SLG-against':'darkblue',
                   'BA-against':'forestgreen', 'HR-A/PA':'tan'}
                st.plotly_chart(create_dotplot(all_stats, player_name, metrics1), use_container_width=True)
                st.write('')
                metrics2 = {'FIP':'darkorange', 'ERA':'dodgerblue', 'WHIP':'navy'}
                st.plotly_chart(create_dotplot(all_stats, player_name, metrics2), use_container_width=True)
                st.write('')
                st.plotly_chart(create_scatter(all_stats, 'BF', 'FIP', player_name), use_container_width=True)
            except: 
                st.warning('no records found')
            st.write('')
            st.info('Data from stats.ncaa.org, valid 2013-2022. Linear Weights for seasons 2013-2021 courtesy of Robert Frey. Note: Linear Weights for 2022 season are average of past five seasons.')
