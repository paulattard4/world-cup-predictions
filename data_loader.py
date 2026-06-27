from io import StringIO
from pathlib import Path

import certifi
import pandas as pd
import requests
import streamlit as st


DATA_DIR = Path("data")


GOOGLE_SHEET_CSV_URLS = {
    "contestants": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=0&single=true&output=csv",
    "matches": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=258089032&single=true&output=csv",
    "match_predictions": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=1642921165&single=true&output=csv",
    "predicted_scorers": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=1874909137&single=true&output=csv",
    "results": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=1939495717&single=true&output=csv",
    "actual_scorers": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=1770710992&single=true&output=csv",
    "group_predictions": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=1810244869&single=true&output=csv",
    "group_results": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=477464182&single=true&output=csv",
    "award_predictions": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=430492069&single=true&output=csv",
    "award_results": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=1695379614&single=true&output=csv",
    "settings": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRV_yHNn4HrPUAdeFAqT22JvCambhRmF-T3zGTj8wqzDc4PExUBLyzcf3iNHeWojWXTU93vvnaUeZD/pub?gid=299914494&single=true&output=csv",
}


@st.cache_data(ttl=30)
def load_csv_file(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_csv_url(url: str) -> pd.DataFrame:
    if not url:
        return pd.DataFrame()

    try:
        response = requests.get(url, timeout=20, verify=certifi.where())
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text), keep_default_na=False)
    except Exception as exc:
        st.error("Could not read Google Sheets CSV URL.")
        st.write(url)
        st.exception(exc)
        return pd.DataFrame()


def load_table(key: str, csv_filename: str) -> pd.DataFrame:
    url = GOOGLE_SHEET_CSV_URLS.get(key, "")

    if url:
        return load_csv_url(url)

    return load_csv_file(csv_filename)


def get_data_source_name() -> str:
    return "Google Sheets published CSV"


def load_all_data() -> dict[str, pd.DataFrame]:
    return {
        "contestants": load_table("contestants", "contestants.csv"),
        "matches": load_table("matches", "matches.csv"),
        "match_predictions": load_table("match_predictions", "match_predictions.csv"),
        "predicted_scorers": load_table("predicted_scorers", "predicted_scorers.csv"),
        "results": load_table("results", "results.csv"),
        "actual_scorers": load_table("actual_scorers", "actual_scorers.csv"),
        "group_predictions": load_table("group_predictions", "group_predictions.csv"),
        "group_results": load_table("group_results", "group_results.csv"),
        "award_predictions": load_table("award_predictions", "award_predictions.csv"),
        "award_results": load_table("award_results", "award_results.csv"),
        "settings": load_table("settings", "settings.csv"),
    }
