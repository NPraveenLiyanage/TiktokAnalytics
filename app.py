import streamlit as st
import pandas as pd
import plotly.express as px

#Load in existing data
df= pd.read_csv('tiktokdata.csv')

#Input
hashtag = st.text_input('search for hashtag here', value="")

#show tabular dataframe in streamlit
df

#plotly viz 
fig = px.histogram(df, x='desc', y='stats_diggCount')
st.plotly_chart(fig, use_container_width=True)