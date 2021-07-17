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
    st.set_page_config(
        page_title="ML/DS Gallery",
        page_icon=(":computer:"),
        layout="centered",
        initial_sidebar_state="auto",
    )

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.sidebar.write("# Navigation")
    selection = st.sidebar.radio("Go to:", list(PAGES.keys()), index=0)
    st.sidebar.info("# Author\n\nRolando Trevino")

    page = PAGES[selection]

    with st.spinner(f"Loading {selection} ..."):
        page.write()


if __name__ == "__main__":
    main()
