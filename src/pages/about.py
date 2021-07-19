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

    st.title("ML/DS Gallery - About")
    st.write("---")
    st.markdown("""
    I decided to start this project by the end of my Master's in Computer Science. I learned to use Streamlit during 
    my Master's thesis, which was to apply Natural Language Processing techniques to online customer service transcripts to discover intents.
    
    The reason is that I have worked on different application of machine learning and data science but
    never stored them in an organized way, and where mostly jupyter notebooks which require a user to 
    have the required packages and their corresponding versions. I came to realize that it would be a good idea to establish a portfolio gathering my projects in this 
    framework due to its ease of use and navigation.

    During my internet exploration for material to add to my thesis framework, I came to discover
    [awesome-streamlit](https://github.com/MarcSkovMadsen/awesome-streamlit), and was able to learn from
    its repository of ideas and implementations. It's an amazing repository, don't hesitate on checking it out!

    I plan on continuously expanding contents on this application to gather fun and interesting projects of mine.

    """)