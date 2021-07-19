"""Home page shown when the user enters the application"""
import streamlit as st
from src.applications.exploratory_analysis.exploratory_analysis import exploratory_analysis_apps
from src.applications.data_visualization.data_visualization import data_visualization_apps
from src.applications.natural_language_processing.natural_language_processing import natural_language_processing_apps
from src.applications.finance.finance import finance_apps

CATEGORIES = {
    "- SELECT CATEGORY -": [],
    "Exploratory Analysis": exploratory_analysis_apps,
    "Data Visualization": data_visualization_apps,
    "Natural Language Processing": natural_language_processing_apps,
    "Finance": finance_apps
}

def write():

    st.markdown(
    f"""
    <style>
        .reportview-container .main .block-container{{
            {f"max-width: 95%"}
        }}
    </style>
    """,
            unsafe_allow_html=True,
    )

    if st.session_state['navigation_current'] != "Gallery":
        st.session_state['navigation_current'] = "Gallery"
        st.session_state['navigation_changed'] = True
    else:
        st.session_state['navigation_changed'] = False

    st.title("ML/DS Gallery - Gallery")
    st.write("---")
    st.sidebar.write("# Gallery")
    select_category = st.sidebar.selectbox("Categories:", list(CATEGORIES.keys()), index=0)

    if select_category != list(CATEGORIES.keys())[0]:
        if st.session_state['navigation_changed'] == True:
            select_application = st.sidebar.selectbox("Applications:", [])
            st.session_state['navigation_changed'] = False
        else:
            select_application = st.sidebar.selectbox("Applications:", list(CATEGORIES[select_category].keys()))

        if select_application != None:
            page = CATEGORIES[select_category][select_application]
            
            with st.spinner(f"Loading {select_application} ..."):
                st.write(f"## {select_application}")
                page()
    else:
        select_application = st.sidebar.selectbox("Applications:", [])
        st.session_state['navigation_changed'] = False