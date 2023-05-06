import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px

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

st.set_page_config(layout='wide')

df = load_csv('data/Electric_Vehicle_Population_Data.csv')

df = df[df['State'] == 'WA']
df['Vehicle Location EXTRACT'] = df['Vehicle Location'].str.extract('.*\((.*)\).*')

df[['LONGITUDE', 'LATITUDE']] = df['Vehicle Location EXTRACT'].str.split(expand=True)

df = df.drop(['Vehicle Location EXTRACT'], axis = 1)

df['LATITUDE'] = pd.to_numeric(df['LATITUDE'])
df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'])

st.title('Electric-Vehicle Ownership in the State of Washington')

#### Sidebar ####
ev_type = st.sidebar.selectbox(label='EV Type', options=['All', 'Battery Electric Vehicle (BEV)', 'Plug-in Hybrid Electric Vehicle (PHEV)'])

make = st.sidebar.selectbox(label='Make', options=get_makes_list(df))
model = st.sidebar.selectbox(label='Model', options=get_models_list(df, make))

year_range = st.sidebar.slider(label='Model Year', min_value=get_min_year(df), max_value=get_max_year(df), value=(2010, 2023))

#### End Sidebar ###

### Content ###
data_tab, washington_tab, range_tab, additional_stats = st.tabs(['Table', 'Washington State', 'Electric Range', 'Additional Statistics'])
filtered_df = get_filtered_df(df, ev_type, make, model, year_range)

with data_tab:
    if len(filtered_df.index) > 0:
        st.dataframe(filtered_df)
    else:
        st.warning('**Warning:** No data found. Change your filters.')

with washington_tab:
    map_df = filtered_df[filtered_df['LATITUDE'].notna() & filtered_df['LONGITUDE'].notna()]
    fig = px.scatter_mapbox(df, lat="LATITUDE", lon="LONGITUDE", zoom=3)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)
with range_tab:
    st.info('**Info:** Data recorded with a **0** electric range are ignored.')

    range_filtered_df = filtered_df[filtered_df['Electric Range'] > 0]

    if model == 'All':    
        st.info('**Info:** Select a model in the sidebar to see statistics of selected model.')

        top_electric_range_chart = alt.Chart(range_filtered_df).mark_bar().encode(
            x=alt.X('mean_range:Q', title='Average Range'),
            y=alt.Y('Model:N', sort='-x'),
            tooltip=['Make', 'Model', alt.Tooltip('mean_range:Q', title='Average Range')]
        ).transform_aggregate(
            mean_range='mean(Electric Range)',
            groupby=['Make', 'Model']
        )

        st.altair_chart(top_electric_range_chart, use_container_width=True)
    else:
        st.info('**Info:** Select All models to see a bar chart of the list of models.')

        st.markdown('<p style="font-size: 1.25rem;"><strong>Statistics:</strong> ' + make.lower().capitalize() + ' ' + model.lower().title() + '</p>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label='Average Range', value=round(np.mean(range_filtered_df['Electric Range'])))
        
        with col2:
            st.metric(label='Median Range', value=round(np.median(range_filtered_df['Electric Range'])))
        
        with col3:
            st.metric(label='Max Range', value=round(np.max(range_filtered_df['Electric Range'])))
        
        with col4:
            st.metric(label='Min Range', value=round(np.min(range_filtered_df['Electric Range'])))