import streamlit as st

# Custom imports
from multipage_object import MultiPage
from views import screener,portfolio,market
# Create an instance of the app
app = MultiPage()


# Add all your applications (pages) here
app.add_page("Screener", screener.load_view)
app.add_page("Portfolio", portfolio.load_view)
app.add_page("Market", market.load_view)


# The main app
app.run()