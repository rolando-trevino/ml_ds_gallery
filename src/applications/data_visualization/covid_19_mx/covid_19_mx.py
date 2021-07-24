"""Home page shown when the user enters the application"""
import streamlit as st
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.express as px
import plotly.graph_objects as go

df = pd.DataFrame()

def write():
    import re
    from datetime import datetime, date
    import json
    from urllib.request import urlopen

    global df

    st.markdown("""
    Simple and easy to interpret dashboard showing new cases over a map, as well as graphs representing: total cases, new cases by day, and new cases by day 
    (moving average of 7 days).
    
    Data corresponding to this app is maintained through Github Actions, via daily download of information from 
    [Mexico's government source for COVID-19](https://www.gob.mx/salud/documentos/datos-abiertos-152127).
    """)

    if len(df) == 0:
        df = pd.read_csv("https://raw.githubusercontent.com/rolando-trevino/ml_ds_gallery/main/data/gallery/data_visualization/covid_19_mx/per_state.csv")
        # df = pd.read_csv("data/gallery/data_visualization/covid_19_mx/per_state.csv")
        df['state'] = df['state'].astype(int)
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(by=['state', 'date'], inplace=True)

    state_list = [
        "(0): - NACIONAL -",
        "(1): AGUASCALIENTES",
        "(2): BAJA CALIFORNIA",
        "(3): BAJA CALIFORNIA SUR",
        "(4): CAMPECHE",
        "(5): COAHUILA",
        "(6): COLIMA",
        "(7): CHIAPAS",
        "(8): CHIHUAHUA",
        "(9): CIUDAD DE MEXICO",
        "(10): DURANGO",
        "(11): GUANAJUATO",
        "(12): GUERRERO",
        "(13): HIDALGO",
        "(14): JALISCO",
        "(15): MEXICO",
        "(16): MICHOACAN",
        "(17): MORELOS",
        "(18): NAYARIT",
        "(19): NUEVO LEON",
        "(20): OAXACA",
        "(21): PUEBLA",
        "(22): QUERETARO",
        "(23): QUINTANA ROO",
        "(24): SAN LUIS POTOSI",
        "(25): SINALOA",
        "(26): SONORA",
        "(27): TABASCO",
        "(28): TAMAULIPAS",
        "(29): TLAXCALA",
        "(30): VERACRUZ",
        "(31): YUCATAN",
    ]
    
    if len(df) > 0:
        date_now = datetime.strftime(pd.to_datetime(df['date'].values[-1]), "%Y-%m-%d")
        st.write(f"Data Date: {date_now}")

        # Overall map
        with urlopen('https://covid19.sinave.gob.mx/coronavirus/Mexico_estados.json') as response:
            Mexico = json.load(response) # Javascrip object notation 

        state_id_map = {}
        for feature in Mexico['features']:
            id_ = feature['id']
            estado_ = feature['properties']['ESTADO']
            state_id_map[id_] = estado_

        df_to_map = df.copy()
        df_to_map.set_index(['state', 'date'], inplace=True)
        df_to_map['new cases'] = df_to_map['positive_symptoms'].diff(1)
        df_to_map['new cases'] = [x if x >= 0 else 0 for x in df_to_map['new cases']]
        df_to_map['Cumulative Cases'] = df_to_map.groupby(level=0)['new cases'].cumsum()
        df_to_map = df_to_map.reset_index().groupby([pd.Grouper(level=0), pd.Grouper(key='date', freq='M')]).sum().reset_index()
        df_to_map['State ID'] = [(str(x).zfill(2)) for x in df_to_map['state']]
        df_to_map['State Name'] = [state_id_map[x] for x in df_to_map['State ID']]
        df_to_map['date'] = pd.to_datetime(df_to_map['date'])
        df_to_map['day'] = df_to_map['date'].dt.day
        df_to_map['month'] = df_to_map['date'].dt.month
        df_to_map['year'] = df_to_map['date'].dt.year
        df_to_map['Date'] = [datetime.strftime(date(y, m, d), "%Y-%m-%d") for (y, m, d) in zip(df_to_map['year'], df_to_map['month'], df_to_map['day'])]

        fig = px.choropleth(
            df_to_map, # database
            locations = 'State ID', #define the limits on the map/geography
            geojson = Mexico, #shape information
            color = "Cumulative Cases", #defining the color of the scale through the database
            hover_name = 'State Name', #the information in the box
            title = 'COVID-19 Cases in Mexico Through Time', #title of the map
            animation_frame  = 'Date',
            width = 1024,
            height = 768
        )

        fig.update_geos(fitbounds = "locations", visible = False)
        last_frame_num = len(fig.frames) -1
        fig.layout['sliders'][0]['active'] = last_frame_num
        fig = go.Figure(data=fig['frames'][-1]['data'], frames=fig['frames'], layout=fig.layout)
        st.plotly_chart(fig, use_container_width=True)
        
        selected_state = st.selectbox("Select state:", state_list, index=0)
        selected_state_int = int(re.findall(r"(\d+)", selected_state)[0])

        if selected_state_int != 0:
            df_filtered = df[df['state'] == selected_state_int].copy()
            df_filtered.rename(columns={"date": "Date", "positive_symptoms": "Positive Cases (Symptoms)", "positive_confirmed": "Positive Cases (Confirmed)"}, inplace=True)
        else:
            df_filtered = df.groupby('date').sum().reset_index()

        df_filtered.rename(columns={"date": "Date", "positive_symptoms": "Positive Cases (Symptoms)", "positive_confirmed": "Positive Cases (Confirmed)"}, inplace=True)

        col1, col2 = st.beta_columns(2)

        col1.write(f"<h2 style=\"text-align:center\">Total Cases</h2>", unsafe_allow_html=True)
        col1.write(f"<p style=\"text-align:center\">{df_filtered['Positive Cases (Symptoms)'].values[-1]:,.0f}</p>", unsafe_allow_html=True)

        col2.write(f"<h2 style=\"text-align:center\">New Cases (7 days)</h2>", unsafe_allow_html=True)
        col2.write(f"<p style=\"text-align:center\">+ {df_filtered['Positive Cases (Confirmed)'].diff(1).values[-7:].sum():,.0f}</p>", unsafe_allow_html=True)
        
        # Cases over time
        fig = px.line(df_filtered, x="Date", y="Positive Cases (Symptoms)", title="Cumulative Positive Cases")
        st.plotly_chart(fig, use_container_width=True)

        # New cases
        df_filtered['New Cases'] = df_filtered['Positive Cases (Symptoms)'].diff(1)
        fig = px.line(df_filtered, x="Date", y="New Cases", title="Daily New Cases")
        st.plotly_chart(fig, use_container_width=True)

        # New cases moving average of 7 days
        df_filtered['Moving Average (7)'] = df_filtered['New Cases'].rolling(window=7).mean()
        fig = px.line(df_filtered, x="Date", y="Moving Average (7)", title="New Cases Moving Average (7 days)")
        st.plotly_chart(fig, use_container_width=True)