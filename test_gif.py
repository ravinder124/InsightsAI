import streamlit as st
import os

st.write("Current working directory:", os.getcwd())
st.write("GIF exists:", os.path.exists("images/brain_thinking.gif"))
st.write("Files in images/:", os.listdir("images"))
st.image("images/brain_thinking.gif", width=120)