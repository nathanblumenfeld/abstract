from collegebaseball import metrics
from collegebaseball import win_pct
from collegebaseball import ncaa_scraper as ncaa
from collegebaseball import boydsworld_scraper as bd

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

from hydralit import HydraApp

from team_history import TeamHistoryApp
from team import TeamApp
from player import PlayerApp
from leaderboards import LeaderboardsApp 
from loading import LoadingApp

favicon = Image.open('assets/favicon_white.jpeg')
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
    app.add_app("Leaderboards", app=LeaderboardsApp(), is_home=True)
    app.add_app('Team History', app=TeamHistoryApp())
    app.add_app("Team Stats", app=TeamApp())
    app.add_app("Player Stats", app=PlayerApp())
    app.add_loader_app(LoadingApp())

    app.run()
