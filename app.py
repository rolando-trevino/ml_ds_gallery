"""Main module for the streamlit app"""

import streamlit as st

import src.pages.home
import src.pages.gallery
import src.pages.about

PAGES = {
    "Home": src.pages.home,
    "Gallery": src.pages.gallery,
    "About": src.pages.about
}


def main():
    st.sidebar.write("# Navigation")

    selection = st.sidebar.radio("Go to:", list(PAGES.keys()))
    page = PAGES[selection]

    with st.spinner(f"Loading {selection} ..."):
        page.write()

    st.sidebar.write("---")
    st.sidebar.info("# Author\n\nRolando Trevino")


if __name__ == "__main__":
    st.set_page_config(
        page_title="ML/DS Gallery",
        page_icon=(":computer:"),
        layout="wide",
        initial_sidebar_state="auto",
    )

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: visible;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    if 'navigation_changed' not in st.session_state and 'navigation_current' not in st.session_state:
        st.session_state['navigation_changed'] = False
        st.session_state['navigation_current'] = None

    main()
