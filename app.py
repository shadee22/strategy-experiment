import streamlit as st
# import  strat2_test as strat2
# import  strat1_test as strat1
import  strat1 as strat1
import strat2 as strat2


# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page", ["Strategy  1", "Strategy 2"])


if page == "Strategy  1":
    strat1.render()
    
if page == "Strategy 2":
    strat2.render()

