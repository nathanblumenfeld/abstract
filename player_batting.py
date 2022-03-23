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
    return pd.read_parquet('collegebaseball/data/players_history_new_3.parquet')

def load_player_options(): 
    df = load_player_lookup()
    df.set_index("stats_player_seq", drop=True, inplace=True)
    dictionary = df.to_dict(orient="index")
    return dictionary
    
def create_scatter(data, metric1, metric2, player):
    data = data.sort_values(by='season', ascending=False)
    data.season = data.season.astype('str')
    fig = px.scatter(data, x=metric1, y=metric2, color='season', template='seaborn', color_discrete_sequence=['#003f5c', '#7a5195', '#ef5675', '#ffa600'])
    fig.update_layout(
        title = str(player)+', '+str(metric2)+' vs '+str(metric1),
        xaxis_title=str(metric1),
        yaxis_title=str(metric2)
    )
    fig.update_traces(marker_size=10)
    return fig

def create_histogram(data, metric, player):
    fig = px.histogram(data, x=metric, color='season', marginal="rug", nbins=50, template="none", color_discrete_sequence=['#003f5c', '#7a5195', '#ef5675', '#ffa600'])
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
        fig.add_trace(go.Scatter(
            x=df[i],
            y=df['season'],
            marker=dict(color=metrics[i], size=12),
            mode="lines+markers",
            name=i))                
        fig.update_layout(title=str(player)+' career stats', xaxis=dict(showgrid=False, showline=False), yaxis=dict(showgrid=True, showline=False, gridwidth=0.5, tickmode = 'linear'), height=len(df.season.unique())*125+125)
        fig.update_yaxes(tickvals=df['season'].unique(), autorange='reversed')
    return fig

class PlayerBattingApp(HydraHeadApp):
    def run(self): 
        player_options = load_player_options()
        with st.form('player_batting'):
            col1, col2, col3 = st.columns([3,.25, 2])
            player_id = col1.selectbox('Player', options=player_options.keys(), 
                                    format_func=lambda x: str(player_options.get(x)['name'])+' | '+str(player_options.get(x)['position_set'])+' | '+str(player_options.get(x)['school_set']+' | '+str(player_options.get(x)['season_set'])), key='player_batting')
            player_name = ncaa._format_names(player_options.get(player_id)['name'])
            col2.write('')
            col3.markdown('#')
            player_batting_submit = col3.form_submit_button('submit')
            
        if player_batting_submit:
            try:
                stats = ncaa.get_career_stats(player_id, 'batting')
                all_stats = metrics.add_batting_metrics(stats).sort_values(by='season')
                rate_stats = all_stats[['season', 'PA', 'wOBA', 'OPS', 'OBP', 'SLG', 'BA', 'ISO', 'K%', 'BB%', 'BABIP', 'HR%']]
                counting_stats = all_stats[['season', 'PA', 'H', '1B', '2B', '3B', 'HR', 'BB', 'IBB', 'K', 'HBP', 'RBI', 'R', 'SF', 'SH']]
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('## Rate Stats')
                rate_stats_csv = convert_df(rate_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(player_name)+'_career_rate_stats_.csv', mime='text/csv')
                hide_dataframe_row_index = """
                        <style>
                        .row_heading.level0 {display:none}
                        .blank {display:none}
                        </style>
                """
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                rate_slice = ['PA', 'wOBA', 'OPS', 'OBP', 'SLG', 'BA', 'BABIP', 'ISO', 'K%', 'BB%', 'HR%']
                st.dataframe(rate_stats.style.format({"PA": '{:.0f}', "wOBA": '{:.3f}', "OPS": '{:.3f}', "OBP": '{:.3f}', "SLG": '{:.3f}', "BA": '{:.3f}', "BABIP": '{:.3f}', "ISO": '{:.3f}', "K%": '{:,.2%}', "BB%": '{:,.2%}', "HR%": '{:,.2%}'}, na_rep="", subset=rate_slice).highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=rate_slice).highlight_min(axis=0, props='color:white; font-weight:bold; background-color:#d45087;', subset=rate_slice))
                st.markdown('#')
                col1, col2, col3 = st.columns([3,2,10])
                col1.markdown('## Counting Stats')
                counting_stats_csv = convert_df(counting_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(player_name)+'_career_counting_stats_.csv', mime='text/csv')
                counting_slice = ['PA', 'H', '1B', '2B', '3B', 'HR', 'BB', 'IBB', 'K', 'HBP', 'RBI', 'R', 'SF', 'SH']
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                st.dataframe(counting_stats.style.highlight_min(axis=0, props='color:white; font-weight:bold; background-color:#d45087;', subset=counting_slice).highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=counting_slice))
                rate_metrics = {'BB%':'#003f5c', 'K%':'#2f4b7c', 'BA':'#665191', 'OBP':'#d45087', 'wOBA':'#f95d6a', 'BABIP':'#ff7c43', 'SLG':'#ffa600'}
                st.plotly_chart(create_dotplot(all_stats, player_name, rate_metrics), use_container_width=True)
                st.write('')           
                st.plotly_chart(create_scatter(all_stats, 'PA', 'wOBA', player_name), use_container_width=True)
                st.write('')
            except: 
                st.warning('no records found')
            st.write('')          
            st.info('Data from stats.ncaa.org, valid 2013-2022. Linear Weights for seasons 2013-2021 courtesy of Robert Frey. Note: Linear Weights for 2022 season are average of past five seasons.')
