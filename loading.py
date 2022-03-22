"""
A custom loader implemented as a HydraHeadApp subclass

Nathan Blumenfeld
Feb 2022
"""
import streamlit as st
from hydralit import HydraHeadApp
from hydralit_components import HyLoader, Loaders

class LoadingApp(HydraHeadApp):
    def __init__(self, title = 'Loader',loader=Loaders.pacman, height=500, primary_color='#0083ff', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self._loader = loader
        self._primary_color = primary_color
        self._height = height

    def run(self,app_target):
        with HyLoader("retrieving data...", loader_name=self._loader, height=self._height, primary_color=self._primary_color):
            app_target.run()

