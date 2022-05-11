import streamlit as st
import utils as utl
import sys,os
sys.path.append("/home/ken/airflowProd/notebook/My_Trader")
from my_libs_py3 import my_trader
from views import screener,portfolio,market,stats_lookup,options,configuration



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
    elif route == "stats_lookup":
        stats_lookup.load_view()
    elif route == "options":
        options.load_view()
    elif route == "configuration":
        configuration.load_view()
    elif route == None:
        screener.load_view()

def tool_sidebar():
    with st.sidebar:
        ticker = st.text_input("Ticker","AAPL")
        st.write(my_trader.beta([ticker])[0])
        pass


if __name__ == "__main__":
    navigation()
    tool_sidebar()