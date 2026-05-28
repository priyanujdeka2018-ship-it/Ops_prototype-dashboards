import streamlit as st


st.set_page_config(
    page_title="Scale Regional Ops Health Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Scale Regional Ops Command Center")
st.subheader("Module A: Regional Operations Health Dashboard")

st.info(
    "Phase 1 scaffold is ready. "
    "Phase 2 will generate synthetic data for regional operations health monitoring."
)

st.markdown(
    """
    ### MVP Modules

    This dashboard will help a regional operations leader monitor:

    - SLA adherence
    - CSAT
    - Backlog
    - Aged backlog
    - Escalation rate
    - Quality score
    - Rework rate
    - Weekly operating risks

    ### Drilldown path

    Region → Work Type → Team → Contributor
    """
)
