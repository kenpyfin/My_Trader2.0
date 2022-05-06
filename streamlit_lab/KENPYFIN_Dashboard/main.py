import streamlit as st
import utils as utl
from views import screener,portfolio,market,options,configuration



st.set_page_config(layout="wide", page_title='Navbar sample')
st.set_option('deprecation.showPyplotGlobalUse', False)
utl.inject_custom_css()
utl.navbar_component()

def navigation():
    route = utl.get_current_route()
    if route == "screener":
        screener.load_view()
    elif route == "portfolio":
        portfolio.load_view()
    elif route == "market":
        market.load_view()
    elif route == "options":
        options.load_view()
    elif route == "configuration":
        configuration.load_view()
    elif route == None:
        screener.load_view()

if __name__ == "__main__":
    navigation()