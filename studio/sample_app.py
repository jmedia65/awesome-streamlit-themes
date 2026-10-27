"""Portable native Streamlit sample for checking an installed theme package."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Installed theme · northstar", page_icon="◈", layout="wide")
with st.sidebar:
    st.title("◈ northstar")
    st.radio("Workspace", ["Overview", "Projects", "Reports", "Settings"], label_visibility="collapsed")
    st.caption("Native Streamlit sample · synthetic data")
    st.text_input("Search projects")

st.caption("WORKSPACE / OVERVIEW")
st.title("A clearer view of your work.")
st.write("Your team's progress, at a glance.")
dashboard, components = st.tabs(["Dashboard", "Components"])
with dashboard:
    metrics = st.columns(3)
    metrics[0].metric("Total revenue", "$48,620", "12.8%", border=True)
    metrics[1].metric("Active projects", "24", "4", border=True)
    metrics[2].metric("Completion rate", "94.2%", "3.1%", border=True)
    with st.container(border=True):
        st.subheader("Revenue over time")
        st.bar_chart(pd.DataFrame({"Revenue": [12, 18, 16, 23, 20, 28, 25, 34]}), height=220,
                     color=st.get_option("theme.primaryColor"))
    with st.container(border=True):
        st.subheader("Recent projects")
        st.button("New project", type="primary")
        st.dataframe(pd.DataFrame({"Project": ["Website refresh", "Customer research"],
            "Owner": ["Alex Kim", "Sam Rivera"], "Status": ["In progress", "Complete"]}), hide_index=True)
with components:
    with st.container(border=True):
        st.subheader("Create a report")
        with st.form("report"):
            st.text_input("Report name", "Monthly overview")
            st.selectbox("Workspace", ["Product team", "Research"])
            st.checkbox("Include a comparison with last month", True)
            st.form_submit_button("Create report", type="primary")
        st.button("Cancel")
    st.code('import streamlit as st\n\nst.title("Made for your next idea.")', language="python")
st.caption("Actual native Streamlit rendering from the installed config and bundled fonts.")
