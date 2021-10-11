"""Home page shown when the user enters the application"""

def covid_19_mx():
    import src.applications.data_visualization.covid_19_mx.covid_19_mx as covid_19_mx
    covid_19_mx.write()

def tweet_counts():
    import src.applications.data_visualization.tweet_counts.tweet_counts as tweet_counts
    tweet_counts.write()

data_visualization_apps = {
    "COVID-19 (Mexico)": covid_19_mx,
    "Tweet counts": tweet_counts
}