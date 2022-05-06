from .view_lib import *
    
def load_view():
    st.title('Top Active')


    # cols_fs = st.multiselect("Display Columns", col_name_fs)

    st.dataframe(top_active(), height=500, width=500)