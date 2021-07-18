"""Home page shown when the user enters the application"""
import streamlit as st
from src.pages.categories import category_exploratory_analysis, category_data_visualization, category_natural_language_processing, category_finance

categories = {
    "Exploratory Analysis": category_exploratory_analysis,
    "Data Visualization": category_data_visualization,
    "Natural Language Processing": category_natural_language_processing,
    "Finance": category_finance
}

def write():
    st.write("# ML/DS Gallery - Gallery")
    st.sidebar.write("# Gallery")
    selection = st.sidebar.selectbox("Categories:", list(categories.keys()), index=0)
    page = categories[selection]

    with st.spinner(f"Loading {selection} ..."):
        page()