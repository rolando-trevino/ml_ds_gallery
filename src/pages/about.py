"""Home page shown when the user enters the application"""
import streamlit as st


def write():
    if st.session_state['navigation_current'] == None:
        st.session_state['navigation_current'] = "About"
        st.session_state['navigation_changed'] = False
    elif (st.session_state['navigation_current'] != "About"):
        st.session_state['navigation_current'] = "About"
        st.session_state['navigation_changed'] = True
    elif (st.session_state['navigation_current'] == "About"):
        st.session_state['navigation_changed'] = False

    st.write("# ML/DS Gallery - About")