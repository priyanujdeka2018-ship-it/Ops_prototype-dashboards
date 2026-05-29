from __future__ import annotations

import streamlit as st

from src.ui_components import install_scale_theme, install_command_center_polish, render_sidebar_brand


st.set_page_config(
    page_title="Scale Regional Ops Command Center",
    page_icon="◆",
    layout="wide",
)

install_scale_theme()
install_command_center_polish()
render_sidebar_brand()

pages = [
    st.Page("pages/10_Operations_Health.py", title="Operations Health"),
    st.Page("pages/20_Escalation_Recurrence.py", title="Escalation Recurrence"),
    st.Page("pages/30_Escalation_Themes.py", title="Escalation Themes"),
    st.Page("pages/40_Quality_Risk.py", title="Quality Risk"),
    st.Page("pages/50_Capacity_SLA.py", title="Capacity SLA"),
]

current_page = st.navigation(pages, position="sidebar")
current_page.run()
