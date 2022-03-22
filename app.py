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

import hydralit as hy
from hydralit import HydraHeadApp
from hydralit import HydraApp

from team_history import TeamHistoryApp
from team_batting import TeamBattingApp
from team_pitching import TeamPitchingApp
from player_batting import PlayerBattingApp
from player_pitching import PlayerPitchingApp

from loading import LoadingApp

favicon = Image.open('assets/favicon.png')
title_img = Image.open('assets/abstract_2x.png')

st.set_page_config(layout='wide', initial_sidebar_state='expanded', page_icon=favicon, page_title="Abstract")

if __name__ == '__main__':
 
    app = HydraApp(
        navbar_animation=False,
        hide_streamlit_markers=False,
        use_navbar=True, 
        navbar_sticky=False,
        use_banner_images=["assets/abstract_0.5x.png", None, {'header':"</br><p style='text-align:center;padding: 0px 0px;color:grey;font-size:100%;'>created by <a href='https://github.com/nathanblumenfeld'>Nathan Blumenfeld</a></p>"}],
        banner_spacing = [20, 40, 15],
        navbar_theme= {'menu_background':'#147DF5', 
                       'option_active':'#FFFFFF', 
                       'txc_inactive':'#FFFFFF', 
                       'txc_active':'#000000'}
    )
    app.add_app('Team History', app=TeamHistoryApp(), is_home=True)
    app.add_app("Team Batting", app=TeamBattingApp())
    app.add_app("Team Pitching", app=TeamPitchingApp())
    app.add_app("Player Batting", app=PlayerBattingApp())
    app.add_app("Player Pitching", app=PlayerPitchingApp())

    app.add_loader_app(LoadingApp())

    app.run()
    
    #     form = st.form(key="history_input")
#     col1, col2, col3, col4, col5 = st.columns([1, .5, 2,.5, .5])
    
#     with col1: 
#         school = form.selectbox('School', options=school_options, key='school_select')
#         school_row = school_lookup.loc[school_lookup.school == school]
#         valid_seasons = school_row.valid_seasons.values[0].copy()
#         valid_seasons.sort()
#         min_season = school_row['min_season'].values[0]
#         max_season = school_row['max_season'].values[0]
#     with col2: 
#         st.write('')
#     with col3: 
#         start, end = form.select_slider('Seasons', options=valid_seasons, value=(min_season, max_season), key='seasons_slider')
#         season_input = [x for x in valid_seasons if ((x >= start) and (x <= end))]
#     with col4: 
#         st.write('')
#     with col5: 
#         st.markdown('#')
#         submit = form.form_submit_button("submit", on_click=form_callback)        
               