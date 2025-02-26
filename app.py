import streamlit as st

# st.set_page_config(layout='wide')
st.set_page_config(page_title="Menu", page_icon="🏠", layout="wide")

# st.sidebar("Menu")

pages = {
    "Home":[st.Page("pages/home.py", icon="🏠", title="Home")],
    "Mpesa Reconciliation": [st.Page("pages/mpesa.py", icon="💸", title="Mpesa Reconciliation")],
    "KES Reconciliation": [
        st.Page("pages/stanbic.py", icon="🏦", title="Stanbic KES Reconciliation"),
        st.Page("pages/dtb.py", icon="🏦", title="DTB KES Reconciliation"),
    ],
    "USD Reconciliation": [
        st.Page("pages/stanbic_usd.py", icon="🏦", title="Stanbic USD Reconciliation"),
    ],
}

pg = st.navigation(pages)
pg.run()
