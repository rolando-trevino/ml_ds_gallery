"""Home page shown when the user enters the application"""
import streamlit as st
from src.applications.exploratory_analysis.exploratory_analysis import exploratory_analysis_apps
from src.applications.data_visualization.data_visualization import data_visualization_apps
from src.applications.natural_language_processing.natural_language_processing import natural_language_processing_apps
from src.applications.finance.finance import finance_apps

def category_exploratory_analysis():
    selection = st.selectbox("Applications:", list(exploratory_analysis_apps.keys()), index=0)
    st.write("---")
    app = exploratory_analysis_apps[selection]

    with st.spinner(f"Loading {selection} ..."):
        st.write(f"# {selection}")
        app()

def category_data_visualization():
    selection = st.selectbox("Applications:", list(data_visualization_apps.keys()), index=0)
    st.write("---")
    app = data_visualization_apps[selection]

    with st.spinner(f"Loading {selection} ..."):
        st.write(f"# {selection}")
        app()

def category_natural_language_processing():
    selection = st.selectbox("Applications:", list(natural_language_processing_apps.keys()), index=0)
    st.write("---")
    app = natural_language_processing_apps[selection]

    with st.spinner(f"Loading {selection} ..."):
        st.write(f"# {selection}")
        app()

def category_finance():
    selection = st.selectbox("Applications:", list(finance_apps.keys()), index=0)
    st.write("---")
    app = finance_apps[selection]

    with st.spinner(f"Loading {selection} ..."):
        st.write(f"# {selection}")
        app()


