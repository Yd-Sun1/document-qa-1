import streamlit as st

st.set_page_config(page_title="Labs")

lab1 = st.Page(
    "Lab1.py",
    title="Lab 1",
    default=True
)

lab2 = st.Page(
    "Lab2.py",
    title="Lab 2"
)

lab3 = st.Page(
    "Lab3.py",
    title="Lab 3"
)

pg = st.navigation(
    {
        "Labs": [lab1, lab2, lab3]
    }
)

pg.run()