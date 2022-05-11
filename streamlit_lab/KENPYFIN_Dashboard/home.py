import streamlit as st

# Custom imports
from multipage_object import MultiPage, choose
from views import screener,portfolio,market
# Create an instance of the app

if choose == "Screener":
    screener.load_view()


