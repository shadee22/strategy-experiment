import streamlit as st
# import  strat2_test as strat2
# import  strat1_test as strat1
import  strat1 as strat1
import strat2 as strat2
import strat3 as strat3
import strat4 as strat4

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page", ["Strategy  1", "Strategy 2", "Strategy 3", "Strategy 4"])

if page == "Strategy  1":
    strat1.render()
    
if page == "Strategy 2":
    strat2.render()

if page == "Strategy 3":
    strat3.render()

if page == "Strategy 4":
    strat4.render()