import streamlit as st
import pandas as pd

#Load in existing data
df= pd.read_csv('tiktokdata.csv')

#Input
hashtag = st.text_input('search for hashtag here', value="")

#show tabular dataframe in streamlit
df