"""
This file is the framework for generating multiple Streamlit applications
through an object oriented framework.
"""

# Import necessary libraries
import streamlit as st
# from streamlit_option_menu import option_menu
# with st.sidebar:
#     choose = option_menu("App Gallery", ["Screener", "Photo Editing", "Project Planning", "Python e-Course", "Contact"],
#                          icons=['house', 'camera fill', 'kanban', 'book','person lines fill'],
#                          menu_icon="app-indicator", default_index=0,orientation="horizontal",
#                          styles={
#         "container": {"padding": "5!important", "background-color": "#fafafa"},
#         "icon": {"color": "orange", "font-size": "25px"},
#         "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
#         "nav-link-selected": {"background-color": "#02ab21"},
#     }
#     )

# Define the multipage class to manage the multiple apps in our program
class MultiPage:
    """Framework for combining multiple streamlit applications."""

    def __init__(self) -> None:
        """Constructor class to generate a list which will store all our applications as an instance variable."""
        self.pages = []

    def add_page(self, title, func) -> None:
        """Class Method to Add pages to the project
        Args:
            title ([str]): The title of page which we are adding to the list of apps

            func: Python function to render this page in Streamlit
        """

        self.pages.append({

            "title": title,
            "function": func
        })

    def run(self):
        # Drodown to select the page to run
        page = st.sidebar.selectbox(
            'App Navigation',
            self.pages,
            format_func=lambda page: page['title'],
        )

        # run the app function
        page['function']()