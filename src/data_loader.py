from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@st.cache_data
def load_table(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.csv"
    if not path.exists():
        st.warning(f"Missing data file: {path}")
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        st.warning(f"Data file is empty: {path}")
        return pd.DataFrame()


def load_tables(*names: str) -> dict[str, pd.DataFrame]:
    return {name: load_table(name) for name in names}
