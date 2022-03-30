import streamlit as st
import pandas as pd
import plotly.express as px

from hydralit import HydraHeadApp

@st.cache(persist=True)
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

@st.cache(allow_output_mutation=True, ttl=60*10, persist=True)
def load_season_stats(season, variant, position, school, minimum, class_year): 
    """
    """
    df = pd.read_parquet('collegebaseball/data/'+variant+'_stats_all_'+str(season)+'_position.parquet')
    res = df 
    if school != 'all': 
        res =  df.loc[df.school == school]

    if position != 'all':
        res = res.loc[res.position == position]
        
    if minimum > 0: 
        if variant == 'batting': 
            res = res.loc[res.PA >= minimum]
        else: 
            res = res.loc[res['IP'] >= minimum]
        
    if class_year != 'all': 
        if 'other' == class_year:
            class_year == 'N/A'
        res = res.loc[res.Yr == class_year]
        
    if variant == 'batting':
        res = res[['name', 'Yr', 'school', 'position', 'PA', 'H', '2B', '3B', 'HR', 'RBI', 'R', 'BB', 'IBB', 'HBP', 'SF', 'SH', 'K', 'GP', 'AB', '1B', 'wOBA', 'OPS', 'OBP', 'SLG', 'BA', 'ISO', 'BABIP', 'HR%', 'K%', 'BB%', 'wRAA', 'wRC']]
    else: 
        res = res[['name', 'Yr', 'school', 'position', 'BF', 'IP', 'FIP', 'ERA', 'WHIP', 'SO', 'BB', 'H', 'HR-A', 'ER', 'R', 'OPS-against', 'OBP-against', 'SLG-against', 'BA-against', 'K/PA', 'K/9', 'BB/PA', 'BB/9', 'HR-A/PA', 'BABIP-against', 'Pitches/PA','IP/App', 'App', 'HB', 'GO', 'FO', 'W', 'L', 'SV']]
    return res

def load_school_options(): 
    df = pd.read_parquet('collegebaseball/data/schools.parquet')
    options = list(df.ncaa_name.unique())
    options.insert(0, 'all')
    return options

def create_dist(df, metric, season):
    fig = px.histogram(df, x=metric, marginal='box', hover_name='name', hover_data=["school"], template="seaborn")
    fig.update_layout(title = str(season)+' '+metric+' distribution', 
                      title_yanchor = "top",
                      title_x =  0.5,
                      xaxis_title=metric,
                      yaxis_title='# of players')                   
    return fig

class LeaderboardsApp(HydraHeadApp):
    def run(self): 
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        season = col1.selectbox('Season', options=range(2013, 2023), index=9, key='season_select')
        stats_type = col5.selectbox('Stats Type', options=['batting', 'pitching'], index=0, key='stats_type_select')
        class_year = col4.selectbox('Class Year', options=['all', 'Fr', 'So', 'Jr', 'Sr', 'other'], index=0, key='stats_type_select')
        if stats_type == 'batting':
            position = col3.selectbox('Position', options=['all', 'INF', 'OF', 'C', 'P', 'DH'], index=0, key='position_select') 
            minimum = col6.number_input('Min. PA', min_value=0, value=20, step=1)
        else: 
            position = col3.selectbox('Position', options=['all', 'P', 'notP'], index=0, key='position_select') 
            minimum = col6.number_input('Min. IP', min_value=0, value=10, step=1)

        school = col2.selectbox('School', options=load_school_options(), index=0, key='school_select')
        try: 
            stats = load_season_stats(season, stats_type, position, school, minimum, class_year)
            hide_dataframe_row_index = """
                    <style>
                    .row_heading.level0 {display:none}
                    .blank {display:none}
                    </style>
            """
            if stats_type == 'batting':
                counting_stats = stats[['name', 'Yr', 'school', 'position', 'PA', 'H', '2B', '3B', 'HR', 'K', 'BB', 'R', 'RBI', 'IBB', 'SF', 'SH', 'HBP']].sort_values(by='H', ascending=False)
                counting_slice = ['PA', 'H', '2B', '3B', 'HR', 'BB', 'K', 'IBB', 'HBP', 'RBI', 'R', 'SF', 'SH']
                rate_stats = stats[['name', 'Yr', 'school', 'position', 'PA', 'wOBA', 'wRC', 'wRAA', 'OPS', 'OBP', 'SLG', 'BA', 'ISO', 'BABIP', 'K%', 'BB%', 'HR%']].sort_values(by='wOBA', ascending=False)
                rate_slice = ['PA', 'wOBA', 'wRC', 'wRAA', 'OPS', 'OBP', 'SLG', 'BA', 'BABIP', 'ISO', 'K%', 'BB%', 'HR%']
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('## Counting Stats')
                counting_stats_csv = convert_df(counting_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(season)+'_'+stats_type+'_counting_stat_leaders_batting'+'_'+str(position)+'_'+str(school)+'_minPA_'+str(minimum)+'.csv', mime='text/csv')
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                st.dataframe(counting_stats.style.highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=counting_slice))
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('## Rate Stats')
                rate_stats_csv = convert_df(rate_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(season)+'_'+stats_type+'_rate_stat_leaders_batting'+'_'+str(position)+'_'+str(school)+'_minPA_'+str(minimum)+'.csv', mime='text/csv')
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                st.dataframe(rate_stats.style.format({"PA": '{:.0f}', "wOBA": '{:.3f}', "wRC": '{:.1f}', "wRAA": '{:.1f}', "OPS": '{:.3f}', "OBP": '{:.3f}', "SLG": '{:.3f}', "BA": '{:.3f}', "BABIP": '{:.3f}', "ISO": '{:.3f}', "K%": '{:,.2%}', "BB%": '{:,.2%}', "HR%": '{:,.2%}'}, na_rep="", subset=rate_slice).highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=rate_slice))
                metric = st.selectbox('select metric', options=['PA', 'H', '2B', '3B', 'HR', 'BB', 'K', 'IBB', 'HBP', 'RBI', 'R', 'SF', 'SH', 'wOBA', 'wRC', 'wRAA', 'OPS', 'OBP', 'SLG', 'BA', 'BABIP', 'ISO', 'K%', 'BB%', 'HR%'], index=13, key='metric_select')
                st.plotly_chart(create_dist(stats, metric, season), use_container_width=True)
            else: 
                rate_stats = stats[['name', 'Yr', 'school', 'IP', 'BF', 'ERA', 'FIP', 'WHIP', 'K/PA', 'BB/PA', 'OPS-against', 'OBP-against', 'SLG-against', 'BA-against', 'BABIP-against', 'Pitches/PA', 'HR-A/PA', 'IP/App']]
                rate_slice = ['IP', 'BF', 'ERA', 'FIP', 'WHIP', 'K/PA', 'BB/PA', 'OPS-against', 'OBP-against', 'SLG-against', 'BA-against', 'BABIP-against', 'Pitches/PA', 'HR-A/PA', 'IP/App']
                counting_stats = stats[['name', 'Yr', 'school', 'IP', 'BF', 'App', 'H', 'SO', 'BB', 'ER', 'R', 'HR-A', 'HB', 'GO', 'FO', 'W', 'L', 'SV']]
                counting_slice = ['IP', 'BF', 'App', 'H', 'SO', 'BB', 'ER', 'R', 'HR-A', 'HB', 'GO', 'FO', 'W', 'L', 'SV']
                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('## Counting Stats')
                counting_stats_csv = convert_df(counting_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=counting_stats_csv, file_name=str(season)+'_'+stats_type+'_counting_stat_leaders_pitching'+'_'+str(position)+'_'+str(school)+'_minIP_'+str(minimum)+'.csv', mime='text/csv')
                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                st.dataframe(counting_stats.style.highlight_max(axis=0, props='color:white; font-weight:bold; background-color:#147DF5;', subset=counting_slice).format({"IP": '{:.1f}'}))

                col1, col2, col3= st.columns([3,2,10])
                col1.markdown('## Rate Stats')
                rate_stats_csv = convert_df(rate_stats)
                col2.markdown('#')
                col2.download_button(label="download as csv", data=rate_stats_csv, file_name=str(season)+'_'+stats_type+'_rate_stat_leaders_pitching'+'_'+str(position)+'_'+str(school)+'_minPA_'+str(minimum)+'.csv', mime='text/csv')

                st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                st.dataframe(rate_stats.style.format({"IP": '{:.1f}', "BF": '{:.0f}', "ERA": '{:.2f}', "FIP": '{:.3f}', "WHIP": '{:.3f}', "K/PA": '{:.3f}', "BB/PA": '{:.3f}', "OPS-against": '{:.3f}', "OBP-against": '{:.3f}', "BABIP-against": '{:.3f}', "SLG-against": '{:.3f}', "BA-against": '{:.3f}', "Pitches/PA": '{:.3f}', "HR-A/PA": '{:.3f}', "IP/App": '{:.3f}'}, na_rep="", subset=rate_slice))

                metric = st.selectbox('select metric', options=['IP', 'BF', 'App', 'H', 'SO', 'BB', 'ER', 'R', 'HR-A', 'HB', 'GO', 'FO', 'W', 'L', 'SV', 'ERA', 'FIP', 'WHIP', 'K/PA', 'BB/PA', 'OPS-against', 'OBP-against', 'SLG-against', 'BA-against', 'BABIP-against', 'Pitches/PA', 'HR-A/PA', 'IP/App'], index=17, key='metric_select')
                st.plotly_chart(create_dist(stats, metric, season), use_container_width=True)
        except:
            st.warning('no records found')
        st.write('')          
        st.info('Data from stats.ncaa.org. Last Updated: 3/30. Linear Weights for seasons 2013-2021 courtesy of Robert Frey. Note: Linear Weights for 2022 season are average of past five seasons.')
