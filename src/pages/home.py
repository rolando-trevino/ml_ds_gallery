"""Home page shown when the user enters the application"""
import streamlit as st


def write():
    if st.session_state['navigation_current'] == None:
        st.session_state['navigation_current'] = "Home"
        st.session_state['navigation_changed'] = False
    elif (st.session_state['navigation_current'] != "Home"):
        st.session_state['navigation_current'] = "Home"
        st.session_state['navigation_changed'] = True
    elif (st.session_state['navigation_current'] == "Home"):
        st.session_state['navigation_changed'] = False

    st.title("ML/DS Gallery - Home")
    st.write("---")
    st.subheader("Welcome!")
    st.markdown("""
    This web application is set to gather fun and interesting projects of mine where I've applied machine learning and data science techniques
    and serve as a portfolio to show topics and tools that I am continuosly becoming familiar with.

    Feel free to navigate and explore the different applications that I'll be uploading in the **Gallery** section, as well as reading the 
    **About** section. Also if you have any question or observation, don't hesitate to contact me through my information found on my github 
    repository 😊
    """)