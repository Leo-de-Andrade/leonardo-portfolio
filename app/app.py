"""
Entry point / router for the multi-page app.

Streamlit's newer navigation API (st.Page + st.navigation, stable since
1.36) lets us define custom page titles and icons in one place, instead of
relying on filenames inside a special "pages/" folder.
"""

import streamlit as st

home_page = st.Page("views/home.py", title="Home", icon="🏠", default=True)
dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="📊")

pg = st.navigation([home_page, dashboard_page])
pg.run()
