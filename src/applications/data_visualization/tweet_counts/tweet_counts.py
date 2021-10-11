"""Home page shown when the user enters the application"""
import streamlit as st
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import json
import time
from datetime import datetime

# colores que sean amigables con gente que padece de daltonismo
# tomado de https://personal.sron.nl/~pault/#sec:qualitative
qualitative_color_blind_safe = {
    "orange": "#EE7733",
    "blue": "#0077BB",
    "cyan": "#33BBEE",
    "magenta": "#EE3377",
    "red": "#CC3311",
    "teal": "#009988",
    "grey": "#BBBBBB"
}

sequential_color_blind_safe = [
    "#E8ECFB", "#DDD8EF", "#D1C1E1", "#C3A8D1", "#B58FC2", "#A778B4", "#9B62A7", "#8C4E99", 
    "#6F4C9B", "#6059A9", "#5568B8", "#4E79C5", "#4D8AC6", "#4E96BC", "#549EB3", "#59A5A9", 
    "#60AB9E", "#69B190", "#77B77D", "#8CBC68", "#A6BE54", "#BEBC48", "#D1B541", "#DDAA3C", 
    "#E49C39", "#E78C35", "#E67932", "#E4632D", "#DF4828", "#DA2222", "#B8221E", "#95211B", 
    "#721E17", "#521A13", "#666666"
]

search_url = "https://api.twitter.com/2/tweets/counts/recent"

def create_headers(bearer_token):
    """Twitter function for auth bearer token
    Args:
        bearer_token (string): bearer token from twitter api
    Returns:
        headers
    """
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params=None):
    """Twitter function to connect to API
    Args:
        url (string): url of desired function from api
        headers (dict): headers containing the auth token
        params (dict, optional): contain extra parameters for function. Defaults to None.
    Raises:
        Exception: if url returned an error when calling the api
    Returns:
        response.json(): json string containing the response from api
    """
    time.sleep(1)
    if params is not None:
        response = requests.request("GET", url, headers=headers, params=params)
    else:
        response = requests.request("GET", url, headers=headers)

    resetdate = datetime.fromtimestamp(int(response.headers["x-rate-limit-reset"]))

    if response.status_code == 429:
        st.write(f"Rate limit reached (Error {response.status_code}). Rate limit reset date: {resetdate}.")
        while datetime.now() < resetdate:
            time.sleep(10)
        if params is not None:
            response = requests.request("GET", url, headers=headers, params=params)
        else:
            response = requests.request("GET", url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
    elif response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()


def create_url():
    """Creates url for consulting a single tweet
    Args:
        None
    Returns:
        url: url used for api
    """
    url = search_url

    return url
   

def write():
    st.markdown("""
    Search the Twitter API and retrieve the number of tweets posted during the last 7 days in the platform.
    """)

    bearer_token = st.text_input("Bearer token:")
    search_query = st.text_input("Search query:", max_chars=1024)
    granularity = st.selectbox("Granularity:", ['minute', 'hour', 'day'], index=2)

    if st.button("Run") and len(bearer_token) > 0 and len(search_query) > 0:
        st.write("---")
        # Optional params: start_time,end_time,since_id,until_id,next_token,granularity
        query_params = {
            "query": search_query,
            "granularity": granularity
        }
        # Extract headers for authentication
        headers = create_headers(bearer_token)
        # Get json response
        json_response = connect_to_endpoint(search_url, headers, query_params)
        # Dump json response to string
        data = json.dumps(json_response, indent=4, sort_keys=True)
        # Load json object from string
        data = json.loads(data)
        # Print total tweet count
        st.write(f"Total tweet count: {data['meta']['total_tweet_count']}")
        # Set json as dataframe
        data = pd.json_normalize(data["data"])
        # Print chart
        fig = px.line(data, 
            x="end", 
            y="tweet_count", 
            title=f"Tweet count last 7 days (granularity: {granularity})",
            labels={"end": "Date", "tweet_count": "Tweet count"},
            color_discrete_sequence=[qualitative_color_blind_safe["blue"]],
            template="plotly"
        )
        st.plotly_chart(fig, use_container_width=True)