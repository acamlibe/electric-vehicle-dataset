import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import datetime

#### Functions/Methods ####

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

def get_makes_list(df):
    unique_makes = df['Make'].unique()

    all_makes = np.insert(unique_makes, 0, 'All')
    return all_makes

def get_models_list(df, make):
    unqiue_makes_for_model = df[df['Make'] == make]['Model'].unique()

    all_models = np.insert(unqiue_makes_for_model, 0, 'All')
    return all_models

def get_min_year(df):
    return df['Model Year'].min().item()

def get_max_year(df):
    return df['Model Year'].max().item()

def get_filtered_df(df, ev_type, make, model, year_range):
    filtered_df = df

    if ev_type != 'All' and ev_type is not None:
        filtered_df = filtered_df[filtered_df['Electric Vehicle Type'] == ev_type]

    if make != 'All' and make is not None:
        filtered_df = filtered_df[filtered_df['Make'] == make]

    if model != 'All' and model is not None:
        filtered_df = filtered_df[filtered_df['Model'] == model]

    if year_range is not None:
        filtered_df = filtered_df[(filtered_df['Model Year'] >= year_range[0]) & (filtered_df['Model Year'] <= year_range[1])]

    return filtered_df

#### End Functions/Methods ####

### Streamlit General ###
st.set_page_config(layout='wide')
st.title('Electric-Vehicle Ownership in the State of Washington')
### End Streamlit General ###

#### Data Wrangling ####

df = load_csv('data/Electric_Vehicle_Population_Data.csv')

df = df[df['State'] == 'WA']
df['Vehicle Location'] = df['Vehicle Location'].str.extract('.*\((.*)\).*')

df[['LONGITUDE', 'LATITUDE']] = df['Vehicle Location'].str.split(expand=True)

df = df.drop(['Vehicle Location'], axis = 1)

df['LATITUDE'] = pd.to_numeric(df['LATITUDE'])
df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'])

gas_df = load_csv('data/Washington_All_Grades_Conventional_Retail_Gasoline_Prices.csv')
gas_df['Month'] = pd.to_datetime(gas_df['Month'], format='%b-%y').dt.date

ev_history_df = load_csv('data/Electric_Vehicle_Population_Size_History.csv')
ev_history_df['Date'] = pd.to_datetime(ev_history_df['Date'], format='%B %d %Y').dt.date

#### End Data Wrangling ####

#### Sidebar ####
st.sidebar.info('Settings reactively change data')
ev_type = st.sidebar.selectbox(label='EV Type', options=['All', 'Battery Electric Vehicle (BEV)', 'Plug-in Hybrid Electric Vehicle (PHEV)'])

make = st.sidebar.selectbox(label='Make', options=get_makes_list(df))
model = st.sidebar.selectbox(label='Model', options=get_models_list(df, make))

year_range = st.sidebar.slider(label='Model Year', min_value=get_min_year(df), max_value=get_max_year(df), value=(2010, 2023))

#### End Sidebar ###

### Content ###
data_tab, washington_tab, range_tab, additional_stats, gas_tab, ev_history_tab = st.tabs(['Data Table', 'Washington State', 'Electric Range', 'EV Type and CAFV Eligibility', 'Gas Price History', 'EV Ownership History'])
filtered_df = get_filtered_df(df, ev_type, make, model, year_range)

with data_tab:
    if len(filtered_df.index) > 0:
        st.dataframe(filtered_df)
    else:
        st.warning('**Warning:** No data found. Change your filters.')

with washington_tab:
    st.header('Map of Washington State')

    map_df = filtered_df[filtered_df['LATITUDE'].notna() & filtered_df['LONGITUDE'].notna()]

    fig = px.scatter_mapbox(map_df, lat="LATITUDE", lon="LONGITUDE", zoom=5)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    top_cities_col, top_counties_col = st.columns(2)

    with top_cities_col:
        st.header('Top 20 Cities')

        top_cities_chart = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X('count:Q', title='City Count'),
            y=alt.Y('City:N', sort=alt.EncodingSortField(field='count', order='descending', op='sum')),
            tooltip=['County', 'City', alt.Tooltip('count:Q', title='City Count')]
        ).transform_aggregate(
            count='count()',
            groupby=['City']
        ).transform_window(
            window=[{'op': 'rank', 'as': 'rank'}],
            sort=[{'field': 'count', 'order': 'descending'}]
        ).transform_filter('datum.rank <= 20')

        st.altair_chart(top_cities_chart, use_container_width=True)
    with top_counties_col:
        st.header('Top 20 Counties')

        top_counties_chart = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X('count:Q', title='County Count'),
            y=alt.Y('County:N', sort=alt.EncodingSortField(field='count', order='descending', op='sum')),
            tooltip=['County', alt.Tooltip('count:Q', title='County Count')]
        ).transform_aggregate(
            count='count()',
            groupby=['County']
        ).transform_window(
            window=[{'op': 'rank', 'as': 'rank'}],
            sort=[{'field': 'count', 'order': 'descending'}]
        ).transform_filter('datum.rank <= 20')

        st.altair_chart(top_counties_chart, use_container_width=True)
    
with range_tab:
    st.info('**Info:** Data recorded with a **0** electric range are ignored.')

    range_filtered_df = filtered_df[filtered_df['Electric Range'] > 0]

    if model == 'All':    
        st.info('**Info:** Select a model in the sidebar to see statistics of selected model.')

        top_electric_range_chart = alt.Chart(range_filtered_df).mark_bar().encode(
            x=alt.X('mean_range:Q', title='Average Range'),
            y=alt.Y('Model:N', sort='-x'),
            tooltip=['Make', 'Model', alt.Tooltip('mean_range:Q', title='Average Range', format='.2f')]
        ).transform_aggregate(
            mean_range='mean(Electric Range)',
            groupby=['Make', 'Model']
        )

        st.altair_chart(top_electric_range_chart, use_container_width=True)
    else:
        st.info('**Info:** Select All models to see a bar chart of the list of models.')

        st.markdown('<p style="font-size: 1.25rem;"><strong>Statistics:</strong> ' + make.lower().capitalize() + ' ' + model.lower().title() + '</p>', unsafe_allow_html=True)

        avg_range_col, median_range_col, max_range_col, min_range_col = st.columns(4)

        with avg_range_col:
            st.metric(label='Average Range', value=round(np.mean(range_filtered_df['Electric Range'])))
        
        with median_range_col:
            st.metric(label='Median Range', value=round(np.median(range_filtered_df['Electric Range'])))
        
        with max_range_col:
            st.metric(label='Max Range', value=round(np.max(range_filtered_df['Electric Range'])))
        
        with min_range_col:
            st.metric(label='Min Range', value=round(np.min(range_filtered_df['Electric Range'])))

with gas_tab:
    st.info('**Info:** Sidebar settings will not affect data on this tab.')
    
    filtered_gas_df = gas_df[gas_df['Month'] >= datetime.date(2015, 1, 1)]

    gas_price_history_chart = alt.Chart(filtered_gas_df).mark_line().encode(
        x=alt.X('yearmonth(Month):T', title='Month'),
        y=alt.Y('Washington All Grades Conventional Retail Gasoline Prices Dollars per Gallon:Q', title='Gas Price ($)', scale=alt.Scale(domain=[2, 5]))
    )

    st.altair_chart(gas_price_history_chart, use_container_width=True)

with ev_history_tab:
    st.info('**Info:** Sidebar settings will not affect data on this tab.')

    ev_history_chart = alt.Chart(ev_history_df).mark_line().encode(
        x=alt.X('yearmonth(Date):T', title='Date'),
        y=alt.Y('Electric Vehicle (EV) Total:Q', title='Electric Vehicle (EV) Count')
    )

    st.altair_chart(ev_history_chart, use_container_width=True)

with additional_stats:
    st.header('Electric Vehicle Type')
    
    bev_count = len(filtered_df[filtered_df['Electric Vehicle Type'] == 'Battery Electric Vehicle (BEV)'])
    phev_count = len(filtered_df[filtered_df['Electric Vehicle Type'] == 'Plug-in Hybrid Electric Vehicle (PHEV)'])

    st.metric(label='Battery Electric Vehicle (BEV)', value=f'{bev_count:,}')
    st.metric(label='Plug-in Hybrid Electric Vehicle (PHEV)', value=f'{phev_count:,}')


    st.header('Clean Alternative Fuel Vehicle (CAFV) Eligibility')
    st.write('Learn more here: https://app.leg.wa.gov/rcw/default.aspx?cite=82.08.9999')

    cafv_eligible_count = len(filtered_df[filtered_df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'] == 'Clean Alternative Fuel Vehicle Eligible'])
    cafv_not_eligible_count = len(filtered_df[filtered_df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'] == 'Not eligible due to low battery range'])
    cafv_unknown_eligibility_count = len(filtered_df[filtered_df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'] == 'Eligibility unknown as battery range has not been researched'])

    st.metric(label='Eligible', value=f'{cafv_eligible_count:,}')
    st.metric(label='Not Eligible (Low Range)', value=f'{cafv_not_eligible_count:,}')
    st.metric(label='Unknown Eligibility', value=f'{cafv_unknown_eligibility_count:,}')
### End Content ###