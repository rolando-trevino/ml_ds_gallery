"""Home page shown when the user enters the application"""
import streamlit as st


def write():
    import re
    from datetime import datetime, date
    import json
    from urllib.request import urlopen

    global df

    st.markdown(
    """
    Simple and easy to interpret dashboard showing new cases over a map, as well as graphs representing: total cases, new cases by day, and new cases by day 
    (moving average of 7 days).
    
    Data corresponding to this app is maintained through Github Actions, via daily download of information from 
    [Mexico's government source for COVID-19](https://www.gob.mx/salud/documentos/datos-abiertos-152127).

    Heroku Link: Pending.

    Repository Link: [COVID-MX](https://github.com/rolando-trevino/COVID_MX).
    """
    )

    