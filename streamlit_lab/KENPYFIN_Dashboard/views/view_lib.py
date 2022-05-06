import streamlit as st
import sys,os
sys.path.append("/home/ken/airflowProd/notebook/My_Trader/")
print(os.path.dirname(os.getcwd()))
from my_libs_py3 import *
pd.set_option("display.max_rows",100)

def clear_multi(attribute):
    a = getattr(st.session_state,attribute)
    a = []
