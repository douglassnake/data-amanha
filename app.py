
import io
import os
from urllib.parse import quote as url_quote
from datetime import datetime, timedelta, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime
from html import unescape
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    requests = None
    REQUESTS_OK = False

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    import yfinance as yf
    YF_OK = True
except Exception:
    YF_OK = False

st.set_page_config(
    page_title="Observatório de Instabilidade Global | Painel institucional",
    page_icon="🌍",
    layout="wide",
)

DEFAULT_CSV = """year,orbital,war,climate,economy,politics,science,demography,health,global_index
1900,0,1,1,1,1,2,1,2,1.25
1901,0,1,1,1,1,2,1,2,1.25
1902,0,1,1,1,1,2,1,2,1.25
1903,0,1,1,1,1,2,1,2,1.25
1904,0,1,1,1,1,2,1,2,1.25
1905,0,1,1,1,1,2,1,2,1.25
1906,0,1,1,1,1,2,1,2,1.25
1907,0,1,1,1,1,2,1,2,1.25
1908,0,1,1,1,1,2,1,2,1.25
1909,0,1,1,1,1,2,1,2,1.25
1910,0,1,1,1,1,2,1,2,1.25
1911,0,1,1,1,1,2,1,2,1.25
1912,0,1,1,1,1,2,1,2,1.25
1913,0,1,1,1,1,2,1,2,1.25
1914,0,3,1,1,1,2,1,2,1.65
1915,0,3,1,1,1,2,1,2,1.65
1916,0,3,1,1,1,2,1,2,1.65
1917,0,3,1,1,5,2,1,2,2.05
1918,0,3,1,1,1,2,1,5,2.1
1919,0,1,1,1,1,2,1,2,1.25
1920,0,1,1,1,1,2,1,2,1.25
1921,0,1,1,1,1,2,1,2,1.25
1922,0,1,1,1,1,2,1,2,1.25
1923,0,1,1,1,1,2,1,2,1.25
1924,0,1,1,1,1,2,1,2,1.25
1925,0,1,1,1,1,3,1,2,1.35
1926,0,1,1,1,1,3,1,2,1.35
1927,0,1,1,1,1,3,1,2,1.35
1928,0,1,1,1,1,3,1,2,1.35
1929,0,1,1,5,1,3,1,2,1.95
1930,0,1,1,5,1,3,1,2,1.95
1931,0,1,1,5,1,3,1,2,1.95
1932,0,1,1,5,1,3,1,2,1.95
1933,0,1,1,1,4,3,1,2,1.65
1934,0,1,1,1,1,3,1,2,1.35
1935,0,1,1,1,1,3,1,2,1.35
1936,0,1,1,1,1,3,1,2,1.35
1937,0,1,1,1,1,3,1,2,1.35
1938,0,1,1,1,1,3,1,2,1.35
1939,0,3,1,1,1,3,1,2,1.75
1940,0,3,1,1,1,3,2,2,1.9
1941,0,3,1,1,1,3,2,2,1.9
1942,0,3,1,1,1,3,2,2,1.9
1943,0,3,1,1,1,3,2,2,1.9
1944,0,3,1,1,1,3,2,2,1.9
1945,0,3,1,1,5,3,2,2,2.3
1946,0,1,1,1,1,3,2,2,1.5
1947,0,1,1,1,1,3,2,2,1.5
1948,0,1,1,1,1,3,2,2,1.5
1949,0,1,1,1,1,3,2,2,1.5
1950,0,2,1,1,1,4,2,2,1.8
1951,0,1,1,1,1,4,2,2,1.6
1952,0,1,1,1,1,4,2,2,1.6
1953,1,1,1,1,1,4,2,2,1.6
1954,0,1,1,1,1,4,2,2,1.6
1955,0,1,1,1,1,4,2,2,1.6
1956,0,1,1,1,1,4,2,2,1.6
1957,0,1,1,1,1,4,2,2,1.6
1958,0,1,1,1,1,4,2,2,1.6
1959,0,1,1,1,1,4,2,2,1.6
1960,0,1,2,1,1,4,2,2,1.75
1961,0,1,2,1,1,4,2,2,1.75
1962,0,1,2,1,4,4,2,2,2.05
1963,0,1,2,1,1,4,2,2,1.75
1964,0,1,2,1,1,4,2,2,1.75
1965,0,1,2,1,1,4,2,2,1.75
1966,0,1,2,1,1,4,2,2,1.75
1967,0,1,2,1,1,4,2,2,1.75
1968,0,2,2,1,1,4,2,2,1.95
1969,0,1,2,1,1,4,2,2,1.75
1970,0,1,2,1,1,4,2,2,1.75
1971,0,1,2,1,1,4,2,2,1.75
1972,0,1,2,1,1,4,2,2,1.75
1973,0,1,2,4,1,4,2,2,2.2
1974,0,1,2,1,1,4,2,2,1.75
1975,0,1,2,1,1,5,2,2,1.85
1976,0,1,2,1,1,5,2,2,1.85
1977,0,1,2,1,1,5,2,2,1.85
1978,0,1,2,1,1,5,2,2,1.85
1979,0,2,2,4,1,5,2,2,2.5
1980,0,2,2,1,1,5,3,2,2.2
1981,0,1,2,1,1,5,3,2,2.0
1982,0,1,2,1,1,5,3,2,2.0
1983,0,1,2,1,1,5,3,2,2.0
1984,0,1,2,1,1,5,3,2,2.0
1985,0,1,2,1,1,5,3,2,2.0
1986,0,1,2,1,1,5,3,2,2.0
1987,0,1,2,1,1,5,3,2,2.0
1988,0,1,2,1,1,5,3,2,2.0
1989,1,1,2,1,4,5,3,2,2.3
1990,0,1,3,1,1,5,3,2,2.15
1991,0,1,3,1,5,5,3,2,2.55
1992,0,1,3,1,1,5,3,2,2.15
1993,0,1,3,1,1,5,3,2,2.15
1994,0,1,3,1,1,5,3,2,2.15
1995,0,1,3,1,1,5,3,2,2.15
1996,0,1,3,1,1,5,3,2,2.15
1997,0,1,3,1,1,5,3,2,2.15
1998,0,1,3,1,1,5,3,2,2.15
1999,0,1,3,1,1,5,3,2,2.15
2000,0,1,3,1,1,5,3,2,2.15
2001,0,2,3,1,1,5,3,2,2.35
2002,0,1,3,1,1,5,3,2,2.15
2003,0,2,3,1,1,5,3,3,2.5
2004,0,1,3,1,1,5,3,2,2.15
2005,0,1,3,1,1,5,3,2,2.15
2006,0,1,3,1,1,5,3,2,2.15
2007,0,1,3,1,1,5,3,2,2.15
2008,0,1,3,5,1,5,3,2,2.75
2009,0,1,3,1,1,5,3,3,2.3
2010,0,1,3,1,1,5,3,2,2.15
2011,0,1,3,1,1,5,3,2,2.15
2012,0,1,3,1,1,5,3,2,2.15
2013,0,1,3,1,1,5,3,2,2.15
2014,0,2,3,1,1,5,3,3,2.5
2015,0,1,3,1,1,5,3,2,2.15
2016,0,1,3,1,1,5,3,2,2.15
2017,0,1,3,1,1,5,3,2,2.15
2018,0,1,3,1,1,5,3,2,2.15
2019,0,1,3,1,1,5,3,2,2.15
2020,0,1,4,5,1,5,4,5,3.5
2021,0,1,4,1,1,5,4,2,2.45
2022,0,2,4,1,4,5,4,2,2.95
2023,0,1,4,1,1,5,4,2,2.45
2024,0,1,4,1,1,5,4,2,2.45
2025,0,1,4,1,1,5,4,2,2.45
2026,1,1,4,1,1,5,4,2,2.45
"""

DIMENSIONS = ["war", "climate", "economy", "politics", "science", "demography", "health"]
LABELS = {
    "orbital": "Orbital",
    "war": "Guerra",
    "climate": "Clima",
    "economy": "Economia",
    "politics": "Política",
    "science": "Ciência",
    "demography": "Demografia",
    "health": "Saúde",
    "global_index": "Índice Global",
    "global_index_calc": "Índice Calculado",
    "year": "Ano",
    "zone": "Zona",
}

MARKET_UNIVERSE = {
    "Energia": {"etfs": ["XLE"], "stocks_us": ["XOM", "CVX", "SLB"], "stocks_br": ["PETR4.SA", "PRIO3.SA", "RECV3.SA"]},
    "Saúde": {"etfs": ["XLV"], "stocks_us": ["LLY", "JNJ", "UNH"], "stocks_br": ["FLRY3.SA", "HAPV3.SA", "RDOR3.SA"]},
    "Utilidades": {"etfs": ["XLU"], "stocks_us": ["NEE", "DUK", "SO"], "stocks_br": ["TAEE11.SA", "EGIE3.SA", "CPLE6.SA"]},
    "Consumo Básico": {"etfs": ["XLP"], "stocks_us": ["PG", "KO", "WMT"], "stocks_br": ["ABEV3.SA", "MDIA3.SA", "ASAI3.SA"]},
    "Tecnologia": {"etfs": ["XLK"], "stocks_us": ["MSFT", "AAPL", "NVDA"], "stocks_br": ["TOTS3.SA", "LWSA3.SA", "POSI3.SA"]},
    "Semicondutores / IA": {"etfs": ["SOXX", "SMH"], "stocks_us": ["NVDA", "AMD", "AVGO"], "stocks_br": ["TOTS3.SA", "POSI3.SA"]},
    "Defesa": {"etfs": ["ITA"], "stocks_us": ["LMT", "RTX", "NOC"], "stocks_br": []},
    "Financeiro": {"etfs": ["XLF"], "stocks_us": ["JPM", "BAC", "GS"], "stocks_br": ["ITUB4.SA", "BBAS3.SA", "BBDC4.SA"]},
    "Industrial": {"etfs": ["XLI"], "stocks_us": ["GE", "CAT", "HON"], "stocks_br": ["WEGE3.SA", "EMBR3.SA", "RAIL3.SA"]},
    "Materiais": {"etfs": ["XLB"], "stocks_us": ["LIN", "FCX", "NUE"], "stocks_br": ["VALE3.SA", "CSNA3.SA", "GGBR4.SA"]},
    "Imobiliário": {"etfs": ["XLRE", "VNQ"], "stocks_us": ["PLD", "AMT", "EQIX"], "stocks_br": ["IGTI11.SA", "MULT3.SA", "ALOS3.SA"]},
    "Consumo Discricionário": {"etfs": ["XLY"], "stocks_us": ["AMZN", "TSLA", "HD"], "stocks_br": ["MGLU3.SA", "LREN3.SA", "PETZ3.SA"]},
}

MACRO_UNIVERSE = {
    "Índices": {
        "S&P 500": "^GSPC", "Nasdaq 100": "^NDX", "Dow Jones": "^DJI", "Russell 2000": "^RUT",
        "Ibovespa": "^BVSP", "Euro Stoxx 50": "^STOXX50E", "DAX": "^GDAXI", "FTSE 100": "^FTSE",
        "CAC 40": "^FCHI", "Nikkei 225": "^N225", "Hang Seng": "^HSI", "Shanghai Composite": "000001.SS",
    },
    "Moedas": {
        "DXY": "DX-Y.NYB", "EUR/USD": "EURUSD=X", "USD/JPY": "JPY=X", "GBP/USD": "GBPUSD=X",
        "USD/BRL": "BRL=X", "USD/CNY": "CNY=X", "USD/MXN": "MXN=X",
    },
    "Cripto": {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", "BNB": "BNB-USD", "XRP": "XRP-USD",
    },
    "Commodities": {
        "Ouro": "GC=F", "Prata": "SI=F", "Petróleo WTI": "CL=F", "Petróleo Brent": "BZ=F",
        "Gás Natural": "NG=F", "Cobre": "HG=F", "Milho": "ZC=F", "Soja": "ZS=F",
    },
}

SECTOR_PROFILES = {
    "Energia": {"base_return": 4.1, "base_risk": 3.0, "style": "Defensivo cíclico", "exposure": {"war": 0.30, "climate": 0.20, "economy": 0.15, "politics": 0.10, "science": 0.05, "demography": 0.10, "health": 0.00}},
    "Saúde": {"base_return": 3.5, "base_risk": 1.9, "style": "Defensivo", "exposure": {"war": 0.10, "climate": 0.10, "economy": 0.10, "politics": 0.05, "science": 0.15, "demography": 0.15, "health": 0.35}},
    "Utilidades": {"base_return": 2.8, "base_risk": 1.7, "style": "Defensivo regulado", "exposure": {"war": 0.05, "climate": 0.20, "economy": 0.10, "politics": 0.10, "science": 0.05, "demography": 0.20, "health": 0.05}},
    "Consumo Básico": {"base_return": 2.9, "base_risk": 1.8, "style": "Defensivo", "exposure": {"war": 0.05, "climate": 0.10, "economy": 0.10, "politics": 0.05, "science": 0.05, "demography": 0.25, "health": 0.15}},
    "Tecnologia": {"base_return": 4.4, "base_risk": 3.8, "style": "Crescimento", "exposure": {"war": -0.05, "climate": 0.05, "economy": 0.25, "politics": 0.05, "science": 0.35, "demography": 0.10, "health": 0.00}},
    "Semicondutores / IA": {"base_return": 4.7, "base_risk": 4.2, "style": "Crescimento agressivo", "exposure": {"war": -0.10, "climate": 0.00, "economy": 0.20, "politics": 0.05, "science": 0.45, "demography": 0.05, "health": 0.00}},
    "Defesa": {"base_return": 4.0, "base_risk": 3.2, "style": "Geopolítico", "exposure": {"war": 0.45, "climate": 0.00, "economy": 0.05, "politics": 0.20, "science": 0.10, "demography": 0.00, "health": 0.00}},
    "Financeiro": {"base_return": 3.3, "base_risk": 3.4, "style": "Cíclico", "exposure": {"war": -0.10, "climate": -0.05, "economy": 0.35, "politics": 0.05, "science": 0.05, "demography": 0.10, "health": 0.00}},
    "Industrial": {"base_return": 3.2, "base_risk": 3.1, "style": "Cíclico", "exposure": {"war": 0.00, "climate": -0.05, "economy": 0.30, "politics": 0.05, "science": 0.10, "demography": 0.10, "health": 0.00}},
    "Materiais": {"base_return": 3.1, "base_risk": 3.3, "style": "Commodities", "exposure": {"war": 0.10, "climate": -0.10, "economy": 0.25, "politics": 0.05, "science": 0.05, "demography": 0.15, "health": 0.00}},
    "Imobiliário": {"base_return": 2.6, "base_risk": 3.7, "style": "Sensível a juros", "exposure": {"war": -0.05, "climate": -0.10, "economy": 0.30, "politics": 0.05, "science": 0.00, "demography": 0.15, "health": 0.00}},
    "Consumo Discricionário": {"base_return": 3.0, "base_risk": 4.0, "style": "Cíclico agressivo", "exposure": {"war": -0.10, "climate": -0.05, "economy": 0.35, "politics": 0.05, "science": 0.10, "demography": 0.05, "health": 0.00}},
}

SIGNAL_RULES = {
    "Risk-on / Risk-off": {"positive": ["Nasdaq 100", "S&P 500", "Bitcoin"], "negative": ["DXY", "Ouro"]},
    "Inflação / Desinflação": {"positive": ["Petróleo Brent", "Petróleo WTI", "Cobre", "Ouro"], "negative": ["Nasdaq 100", "Euro Stoxx 50"]},
    "Dólar forte / fraco": {"positive": ["DXY", "USD/JPY", "USD/BRL"], "negative": ["EUR/USD", "GBP/USD", "Ouro"]},
    "Commodities pressionando / aliviando": {"positive": ["Petróleo Brent", "Gás Natural", "Milho", "Soja"], "negative": ["Nasdaq 100"]},
    "Cripto confirmando / divergindo": {"positive": ["Bitcoin", "Ethereum", "Solana"], "negative": ["DXY"]},
}

# ---------- Core ----------
def load_default_data():
    dataset_path = Path(__file__).resolve().parent / "data" / "dataset_global_1900_2026.csv"
    if dataset_path.is_file():
        return pd.read_csv(dataset_path)
    return pd.read_csv(io.StringIO(DEFAULT_CSV))

def normalize_score(series):
    return pd.to_numeric(series, errors="coerce").fillna(0).clip(0, 5)

def compute_index(df, weights):
    result = df.copy()
    total = sum(weights.values()) if sum(weights.values()) else 1.0
    result["global_index_calc"] = sum(normalize_score(result[c]) * w for c, w in weights.items()) / total
    return result

def classify_zone(value):
    if value < 1.5:
        return "Estabilidade"
    if value < 2.2:
        return "Transição"
    if value < 3.0:
        return "Instabilidade"
    return "Zona crítica"

def ensure_columns(df):
    out = df.copy()
    for col in ["year", "orbital"] + DIMENSIONS:
        if col not in out.columns:
            out[col] = 0
    if "global_index" not in out.columns:
        out["global_index"] = np.nan
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out = out.dropna(subset=["year"]).copy()
    out["year"] = out["year"].astype(int)
    for col in ["orbital"] + DIMENSIONS + ["global_index"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.sort_values("year").reset_index(drop=True)

# ---------- Forecast ----------
def moving_average_forecast(years, values, horizon, window):
    y = pd.Series(values).dropna().astype(float)
    if len(y) == 0:
        return pd.DataFrame(columns=["year", "forecast", "model"])
    w = max(2, min(window, len(y)))
    base = float(y.tail(w).mean())
    future_years = np.arange(int(years.max()) + 1, int(years.max()) + horizon + 1)
    return pd.DataFrame({"year": future_years, "forecast": base, "model": f"Média móvel ({w})"})

def linear_regression_forecast(years, values, horizon):
    mask = ~np.isnan(values)
    x = years[mask].astype(float)
    y = values[mask].astype(float)
    if len(x) < 2:
        return pd.DataFrame(columns=["year", "forecast", "model"])
    coeffs = np.polyfit(x, y, 1)
    future_years = np.arange(int(years.max()) + 1, int(years.max()) + horizon + 1)
    return pd.DataFrame({"year": future_years, "forecast": coeffs[0] * future_years + coeffs[1], "model": "Regressão linear"})

def polynomial_forecast(years, values, horizon, degree):
    mask = ~np.isnan(values)
    x = years[mask].astype(float)
    y = values[mask].astype(float)
    max_degree = min(max(2, int(degree)), max(1, len(x) - 1))
    if len(x) < 3 or max_degree < 2:
        return pd.DataFrame(columns=["year", "forecast", "model"])
    coeffs = np.polyfit(x, y, max_degree)
    future_years = np.arange(int(years.max()) + 1, int(years.max()) + horizon + 1)
    return pd.DataFrame({"year": future_years, "forecast": np.polyval(coeffs, future_years), "model": f"Polinomial grau {max_degree}"})

def exponential_smoothing_forecast(years, values, horizon, alpha):
    y = pd.Series(values).dropna().astype(float).tolist()
    if len(y) == 0:
        return pd.DataFrame(columns=["year", "forecast", "model"])
    level = y[0]
    for val in y[1:]:
        level = alpha * val + (1 - alpha) * level
    future_years = np.arange(int(years.max()) + 1, int(years.max()) + horizon + 1)
    return pd.DataFrame({"year": future_years, "forecast": level, "model": f"Suavização exp. (α={alpha:.2f})"})

def clamp_forecast(df):
    out = df.copy()
    if not out.empty:
        out["forecast"] = out["forecast"].clip(0, 5)
    return out

# ---------- Scenarios ----------
def build_scenario_df(latest_row, deltas, years_ahead, weights, mode):
    rows = []
    base_vals = {dim: float(latest_row[dim]) for dim in DIMENSIONS}
    for step in range(1, years_ahead + 1):
        vals = {}
        for dim in DIMENSIONS:
            if mode == "Choque único":
                applied = deltas[dim] if step == 1 else 0
            elif mode == "Mudança permanente":
                applied = deltas[dim]
            else:
                applied = deltas[dim] * (step / years_ahead)
            vals[dim] = float(np.clip(base_vals[dim] + applied, 0, 5))
        weighted = sum(vals[d] * weights[d] for d in DIMENSIONS)
        total = sum(weights.values()) if sum(weights.values()) else 1.0
        rows.append({"year": int(latest_row["year"]) + step, **vals, "scenario_index": weighted / total})
    out = pd.DataFrame(rows)
    if not out.empty:
        out["zone"] = out["scenario_index"].apply(classify_zone)
    return out

# ---------- Patterns ----------
def detect_change_points(view, sensitivity=1.0):
    s = view[["year", "global_index_calc"]].copy()
    s["delta"] = s["global_index_calc"].diff()
    abs_delta = s["delta"].abs().dropna()
    if abs_delta.empty:
        return pd.DataFrame(columns=["year", "delta", "global_index_calc", "magnitude"])
    threshold = abs_delta.mean() + sensitivity * abs_delta.std(ddof=0)
    cps = s[s["delta"].abs() >= threshold][["year", "delta", "global_index_calc"]].copy()
    cps["magnitude"] = cps["delta"].abs()
    return cps.sort_values("magnitude", ascending=False)

def detect_dominant_cycle(values):
    clean = pd.Series(values).dropna().astype(float).to_numpy()
    if len(clean) < 8:
        return pd.DataFrame(columns=["period_years", "amplitude"])
    centered = clean - clean.mean()
    fft_vals = np.fft.rfft(centered)
    freqs = np.fft.rfftfreq(len(centered), d=1.0)
    mask = freqs > 0
    freqs = freqs[mask]
    amps = np.abs(fft_vals[mask])
    periods = 1 / freqs
    out = pd.DataFrame({"period_years": periods, "amplitude": amps})
    out = out.replace([np.inf, -np.inf], np.nan).dropna()
    out = out[(out["period_years"] >= 2) & (out["period_years"] <= max(2, len(clean)/1.5))]
    return out.sort_values("amplitude", ascending=False).head(10)

def assign_regimes(view):
    out = view.copy()
    bins = [-np.inf, 1.5, 2.2, 3.0, np.inf]
    labels = ["Estável", "Transição", "Instável", "Crítico"]
    out["regime"] = pd.cut(out["global_index_calc"], bins=bins, labels=labels)
    return out

def get_driver_table(view):
    long_df = view.melt(id_vars=["year"], value_vars=DIMENSIONS, var_name="dimension", value_name="value")
    idx = long_df.groupby("year")["value"].idxmax()
    driver = long_df.loc[idx].copy()
    driver["dimension"] = driver["dimension"].map(LABELS)
    return driver.rename(columns={"dimension": "driver", "value": "driver_value"}).sort_values("year")

# ---------- Sector rotation ----------
def calculate_sector_rotation(latest_row):
    rows = []
    latest_vals = {dim: float(latest_row[dim]) for dim in DIMENSIONS}
    instability = float(latest_row["global_index_calc"])
    for sector, meta in SECTOR_PROFILES.items():
        raw = sum(latest_vals[d] * meta["exposure"][d] for d in DIMENSIONS)
        upside = min(5.0, max(0.0, meta["base_return"] + 0.22 * raw - 0.08 * instability))
        risk = min(5.0, max(0.0, meta["base_risk"] + 0.18 * instability - 0.10 * upside))
        efficiency = upside / max(risk, 0.5)
        rows.append({"Setor": sector, "Estilo": meta["style"], "Retorno_potencial": round(upside, 2), "Risco_estimado": round(risk, 2), "Eficiência": round(efficiency, 2)})
    return pd.DataFrame(rows).sort_values(["Eficiência", "Retorno_potencial"], ascending=False).reset_index(drop=True)

def suggest_portfolio(sector_df, profile):
    cfg = {
        "Conservador": {"risk_weight": 0.70, "return_weight": 0.30},
        "Balanceado": {"risk_weight": 0.50, "return_weight": 0.50},
        "Agressivo": {"risk_weight": 0.30, "return_weight": 0.70},
    }[profile]
    df = sector_df.copy()
    df["score_alloc"] = cfg["return_weight"] * df["Retorno_potencial"] + cfg["risk_weight"] * (5 - df["Risco_estimado"])
    df["score_alloc"] = df["score_alloc"].clip(lower=0.01)
    df["Alocação_%"] = 100 * df["score_alloc"] / df["score_alloc"].sum()
    return df.sort_values("Alocação_%", ascending=False).reset_index(drop=True)

# ---------- Market data ----------
@st.cache_data(ttl=900, show_spinner=False)
def download_prices(tickers, period="2y", interval="1d"):
    if not YF_OK or not tickers:
        return pd.DataFrame()
    try:
        data = yf.download(tickers=tickers, period=period, interval=interval,
                           auto_adjust=True, progress=False, group_by="ticker", threads=True)
    except Exception:
        return pd.DataFrame()
    if data is None or len(data) == 0:
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        closes = {}
        for t in tickers:
            if (t, "Close") in data.columns:
                closes[t] = data[(t, "Close")]
        return pd.DataFrame(closes)
    if "Close" in data.columns and len(tickers) == 1:
        return pd.DataFrame({tickers[0]: data["Close"]})
    return pd.DataFrame()

def perf_stats_from_prices(prices):
    prices = prices.dropna(how="all")
    if prices.empty:
        return pd.DataFrame()
    rows = []
    for ticker in prices.columns:
        s = prices[ticker].dropna()
        if len(s) < 25:
            continue
        daily = s.pct_change().dropna()
        def ret(n):
            return (s.iloc[-1] / s.iloc[max(0, len(s)-n)] - 1) if len(s) >= n else np.nan
        drawdown = (s / s.cummax() - 1).min()
        rows.append({
            "Ticker": ticker,
            "Preço": s.iloc[-1],
            "Ret_1M": ret(22),
            "Ret_3M": ret(63),
            "Ret_6M": ret(126),
            "Ret_12M": ret(252),
            "Vol_3M": daily.tail(63).std() * np.sqrt(252) if len(daily) >= 20 else np.nan,
            "Max_Drawdown": drawdown,
        })
    return pd.DataFrame(rows)

def get_market_table(sector_df, market_scope):
    rows = []
    for _, r in sector_df.iterrows():
        m = MARKET_UNIVERSE.get(r["Setor"], {})
        tickers = m.get("etfs", []) if market_scope == "ETFs" else m.get("stocks_us", []) if market_scope == "Ações EUA" else m.get("stocks_br", [])
        for t in tickers:
            rows.append({"Setor": r["Setor"], "Ticker": t, "Estilo": r["Estilo"], "Retorno_potencial_modelo": r["Retorno_potencial"], "Risco_modelo": r["Risco_estimado"], "Eficiência_modelo": r["Eficiência"]})
    return pd.DataFrame(rows)

def blend_market_and_model(model_df, market_stats):
    if model_df.empty or market_stats.empty:
        return pd.DataFrame()
    out = model_df.merge(market_stats, on="Ticker", how="left")
    out["Score_operacional"] = (
        0.45 * out["Eficiência_modelo"]
        + 0.25 * out["Ret_3M"].fillna(0)
        + 0.20 * out["Ret_6M"].fillna(0)
        - 0.20 * out["Vol_3M"].fillna(0)
        + 0.10 * out["Ret_12M"].fillna(0)
        + 0.05 * out["Max_Drawdown"].fillna(0)
    )
    return out.sort_values("Score_operacional", ascending=False).reset_index(drop=True)

# ---------- Macro global ----------
def build_macro_ticker_table():
    rows = []
    for group, mapping in MACRO_UNIVERSE.items():
        for name, ticker in mapping.items():
            rows.append({"Grupo": group, "Ativo": name, "Ticker": ticker})
    return pd.DataFrame(rows)

def build_macro_rank(stats_df, macro_map):
    if stats_df.empty:
        return pd.DataFrame()
    out = macro_map.merge(stats_df, on="Ticker", how="left")
    out["Score_macro"] = (
        0.35 * out["Ret_3M"].fillna(0)
        + 0.25 * out["Ret_6M"].fillna(0)
        + 0.15 * out["Ret_12M"].fillna(0)
        - 0.20 * out["Vol_3M"].fillna(0)
        + 0.05 * out["Max_Drawdown"].fillna(0)
    )
    return out.sort_values("Score_macro", ascending=False).reset_index(drop=True)

# ---------- Signals ----------
def signal_direction(value, pos_thr=0.02, neg_thr=-0.02):
    if pd.isna(value):
        return "neutro"
    if value >= pos_thr:
        return "positivo"
    if value <= neg_thr:
        return "negativo"
    return "neutro"

def build_signal_table(macro_rank):
    if macro_rank.empty:
        return pd.DataFrame()
    score_by_name = {row["Ativo"]: row["Ret_3M"] for _, row in macro_rank.iterrows()}
    rows = []
    for signal_name, cfg in SIGNAL_RULES.items():
        pos_vals = [score_by_name.get(x, np.nan) for x in cfg["positive"]]
        neg_vals = [score_by_name.get(x, np.nan) for x in cfg["negative"]]
        pos_mean = np.nanmean(pos_vals) if len(pos_vals) else np.nan
        neg_mean = np.nanmean(neg_vals) if len(neg_vals) else np.nan
        score = pos_mean - neg_mean if pd.notna(pos_mean) and pd.notna(neg_mean) else np.nan
        rows.append({"Sinal": signal_name, "Score": score, "Leitura": signal_direction(score), "Positivos": ", ".join(cfg["positive"]), "Negativos": ", ".join(cfg["negative"])})
    return pd.DataFrame(rows).sort_values("Score", ascending=False)

def macro_summary_text(signal_df):
    if signal_df.empty:
        return "Sem dados suficientes para sinais macro."
    parts = [f"{row['Sinal']}: {row['Leitura']}" for _, row in signal_df.iterrows()]
    return " | ".join(parts)



# ---------- Mercado verificável v9: dados reais e qualidade da fonte ----------
# Coinbase: último negócio em bolsa. Yahoo: barras indicativas, possivelmente atrasadas.
# A ativação de dados proprietários em painel público exige licença de exibição.
LIVE_UNIVERSES = {
    "Panorama": [
        ("Bitcoin", "BTC-USD", "Coinbase", "USD"),
        ("Ethereum", "ETH-USD", "Coinbase", "USD"),
        ("S&P 500", "^GSPC", "Yahoo", "pontos"),
        ("Nasdaq 100", "^NDX", "Yahoo", "pontos"),
        ("Ibovespa", "^BVSP", "Yahoo", "pontos"),
        ("USD/BRL", "BRL=X", "Yahoo", "BRL por USD"),
        ("Ouro (futuro)", "GC=F", "Yahoo", "USD/onça"),
        ("Brent (futuro)", "BZ=F", "Yahoo", "USD/barril"),
    ],
    "Índices": [(n, t, "Yahoo", "pontos") for n,t in MACRO_UNIVERSE["Índices"].items()],
    "Câmbio": [(n, t, "Yahoo", "unidade do par") for n,t in MACRO_UNIVERSE["Moedas"].items()],
    "Criptomoedas": [
        (n, t, "Coinbase", "USD") for n,t in [
            ("Bitcoin","BTC-USD"),("Ethereum","ETH-USD"),("Solana","SOL-USD"),
            ("XRP","XRP-USD"),("Dogecoin","DOGE-USD")
        ]
    ],
    "Commodities": [(n,t,"Yahoo","unidade do contrato") for n,t in MACRO_UNIVERSE["Commodities"].items()],
    "Ações e ETFs": [(n,t,"Yahoo",u) for n,t,u in [
        ("S&P 500 ETF","SPY","USD"),("Energia ETF","XLE","USD"),
        ("Tecnologia ETF","XLK","USD"),("Saúde ETF","XLV","USD"),
        ("Apple","AAPL","USD"),("Microsoft","MSFT","USD"),
        ("NVIDIA","NVDA","USD"),("Petrobras PN","PETR4.SA","BRL"),
        ("Vale ON","VALE3.SA","BRL")
    ]],
}
COINBASE_ALLOWED = {"BTC-USD","ETH-USD","SOL-USD","XRP-USD","DOGE-USD"}
LICENSED_US_TICKERS = {"SPY","XLE","XLK","XLV","AAPL","MSFT","NVDA"}


def valid_market_price(value):
    try:
        number = float(value)
        return number if np.isfinite(number) and number > 0 else None
    except (ValueError, TypeError, OverflowError):
        return None


def market_timestamp(value):
    if value is None or value == "":
        return None
    try:
        ts = pd.to_datetime(value, utc=True, errors="coerce")
        return None if pd.isna(ts) else ts.to_pydatetime()
    except (ValueError, TypeError, OverflowError):
        return None


def age_description(ts, threshold_seconds):
    if ts is None:
        return "Horário da fonte indisponível"
    age = (datetime.now(timezone.utc) - ts).total_seconds()
    if age < -300:
        return "Horário inconsistente"
    return "Observação recente" if age <= threshold_seconds else "Sem observação recente / mercado fechado"


def parse_coinbase_trade(symbol, payload):
    if symbol not in COINBASE_ALLOWED or not isinstance(payload, dict):
        return None
    p = valid_market_price(payload.get("price"))
    ts = market_timestamp(payload.get("time"))
    if p is None or ts is None:
        return None
    return {
        "Ticker": symbol, "Preço": p, "Última observação (UTC)": ts.isoformat(),
        "Fonte": "Coinbase Exchange", "Modalidade": "Último negócio informado",
        "Qualidade": age_description(ts, 180),
        "Link": "https://api.exchange.coinbase.com/products/" + symbol + "/ticker"
    }


@st.cache_data(ttl=30, show_spinner=False)
def fetch_coinbase_trade(symbol):
    if not REQUESTS_OK or symbol not in COINBASE_ALLOWED:
        return None
    try:
        response = requests.get(
            "https://api.exchange.coinbase.com/products/" + symbol + "/ticker",
            headers={"Accept": "application/json", "User-Agent": "DataAmanhaObservatorio/1.0"},
            timeout=(3, 7),
        )
        response.raise_for_status()
        return parse_coinbase_trade(symbol, response.json())
    except (requests.RequestException, ValueError):
        return None


@st.cache_data(ttl=120, show_spinner=False)
def fetch_yahoo_intraday(tickers):
    if not YF_OK or not tickers:
        return pd.DataFrame()
    try:
        raw = yf.download(
            tickers=list(tickers), period="5d", interval="5m", group_by="ticker",
            auto_adjust=False, progress=False, threads=False, timeout=12
        )
    except Exception:
        return pd.DataFrame()
    if raw is None or raw.empty:
        return pd.DataFrame()
    data = {}
    for ticker in tickers:
        series = None
        if isinstance(raw.columns, pd.MultiIndex):
            if (ticker, "Close") in raw.columns:
                series = raw[(ticker, "Close")]
            elif ("Close", ticker) in raw.columns:
                series = raw[("Close", ticker)]
        elif len(tickers) == 1 and "Close" in raw.columns:
            series = raw["Close"]
        if series is not None:
            series = pd.to_numeric(series, errors="coerce").dropna()
            series = series[np.isfinite(series) & (series > 0)]
            if len(series):
                data[ticker] = series
    return pd.DataFrame(data)


def parse_yahoo_bar(ticker, bars):
    bars = pd.to_numeric(bars, errors="coerce").dropna()
    bars = bars[np.isfinite(bars) & (bars > 0)]
    if bars.empty:
        return None
    idx = pd.Timestamp(bars.index[-1])
    # Sem timezone informado não é correto derivar uma hora UTC.
    ts = idx.tz_convert("UTC").to_pydatetime() if idx.tzinfo is not None else None
    return {
        "Ticker": ticker, "Preço": float(bars.iloc[-1]),
        "Última observação (UTC)": ts.isoformat() if ts else "Fuso não informado",
        "Fonte": "Yahoo Finance / yfinance",
        "Modalidade": "Barra indicativa de 5 min (pode ter atraso)",
        "Qualidade": age_description(ts, 1200),
        "Link": "https://finance.yahoo.com/quote/" + url_quote(ticker, safe="")
    }


@st.cache_data(ttl=120, show_spinner=False)
def fetch_licensed_twelve_quotes(tickers, secret):
    if not REQUESTS_OK or not secret:
        return {}
    result = {}
    for symbol in tuple(tickers)[:6]:
        if symbol not in LICENSED_US_TICKERS:
            continue
        try:
            res = requests.get(
                "https://api.twelvedata.com/quote",
                headers={"Authorization": "apikey " + secret},
                params={"symbol": symbol}, timeout=(3, 7),
            )
            res.raise_for_status()
            item = res.json()
            if not isinstance(item, dict) or item.get("status") == "error":
                continue
            price = valid_market_price(item.get("close"))
            if price is None:
                continue
            ts = market_timestamp(item.get("timestamp"))
            result[symbol] = {
                "Ticker": symbol, "Preço": price,
                "Última observação (UTC)": ts.isoformat() if ts else "Não informado",
                "Fonte": "Twelve Data (licença de exibição)",
                "Modalidade": "Segundo cobertura e plano contratado",
                "Qualidade": age_description(ts, 300),
                "Link": "https://twelvedata.com/docs"
            }
        except (requests.RequestException, ValueError):
            continue
    return result


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bcb_reference():
    """Selic/meta SGS 432 e IPCA mensal SGS 433; referências, não ticks."""
    result = []
    if not REQUESTS_OK:
        return result
    for name, code, unit in [("Meta Selic",432,"% a.a."),("IPCA mensal",433,"% no mês")]:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados/ultimos/1?formato=json"
        try:
            response = requests.get(url, timeout=(3,7))
            response.raise_for_status()
            data = response.json()
            item = data[-1] if isinstance(data,list) and data else None
            if not isinstance(item,dict):
                continue
            value = float(str(item.get("valor","")).replace(",","."))
            if np.isfinite(value):
                result.append({"Indicador":name,"Valor":value,"Unidade":unit,
                               "Referência":item.get("data","N/D"),"Fonte":url})
        except (requests.RequestException,ValueError,TypeError):
            pass
    return pd.DataFrame(result)


def assemble_live_market(group, licensed=False, secret=""):
    wanted = LIVE_UNIVERSES[group]
    tickers = tuple(t for n,t,p,u in wanted if p == "Yahoo")
    yahoo = fetch_yahoo_intraday(tickers) if tickers else pd.DataFrame()
    twelve = fetch_licensed_twelve_quotes(
        tuple(t for t in tickers if t in LICENSED_US_TICKERS), secret
    ) if licensed and secret else {}
    records = []
    for name, ticker, provider, unit in wanted:
        row = None
        if provider == "Coinbase":
            row = fetch_coinbase_trade(ticker)
        elif ticker in twelve:
            row = twelve[ticker]
        elif ticker in yahoo.columns:
            row = parse_yahoo_bar(ticker, yahoo[ticker])
        if row:
            records.append({**row,"Ativo":name,"Unidade":unit})
    return pd.DataFrame(records)


@st.fragment(run_every="60s")
def live_market_panel():
    st.subheader("Mercado observado — sem preços inventados")
    st.warning("A hora da consulta não é a hora da negociação. Cripto: último negócio Coinbase. Ações, ETFs, índices, moedas e futuros: dados indicativos Yahoo, possivelmente atrasados. Não use para executar ordens.")
    group = st.selectbox("Mercado", list(LIVE_UNIVERSES), key="live_universe")
    if st.button("Atualizar agora", key="live_force_refresh"):
        fetch_coinbase_trade.clear()
        fetch_yahoo_intraday.clear()
        fetch_licensed_twelve_quotes.clear()
        fetch_bcb_reference.clear()
    secret = os.environ.get("TWELVE_DATA_API_KEY", "")
    redisplay_allowed = os.environ.get("MARKET_PUBLIC_DISPLAY_LICENSED", "").lower() in ("yes","true","1")
    quotes = assemble_live_market(group, redisplay_allowed, secret)
    now = datetime.now(timezone.utc).astimezone(ZoneInfo("America/Sao_Paulo"))
    st.caption("Consulta em " + now.strftime("%d/%m/%Y %H:%M:%S (Brasília)") + " · atualização automática a cada 60 s durante a sessão do painel")
    a,b,c = st.columns(3)
    a.metric("Ativos selecionados", len(LIVE_UNIVERSES[group]))
    b.metric("Com cotação da fonte", len(quotes))
    c.metric("Indisponíveis", len(LIVE_UNIVERSES[group])-len(quotes))
    if quotes.empty:
        st.error("Nenhuma fonte retornou cotação válida. O painel não substitui ausências por zeros ou estimativas.")
    else:
        for offset in range(0, min(4,len(quotes)), 4):
            cols = st.columns(min(4,len(quotes)-offset))
            for j,col in enumerate(cols):
                row = quotes.iloc[offset+j]
                col.metric(row["Ativo"], f"{row['Preço']:,.2f}", row["Unidade"], delta_color="off")
        fields = ["Ativo","Ticker","Preço","Unidade","Fonte","Modalidade","Última observação (UTC)","Qualidade","Link"]
        st.dataframe(quotes[fields], use_container_width=True, hide_index=True,
            column_config={"Link": st.column_config.LinkColumn("Ver fonte")})
        st.download_button("Exportar cotações reais (CSV)",
            quotes.to_csv(index=False).encode("utf-8-sig"),
            file_name="data_amanha_cotacoes_verificadas.csv",
            mime="text/csv", key="download_live_market")
        st.caption("Índices em pontos; câmbio conforme orientação do par (USD/BRL = reais por dólar); commodities são contratos futuros, não preços à vista.")
    st.markdown("#### Referências oficiais brasileiras")
    ref = fetch_bcb_reference()
    if ref.empty:
        st.info("Banco Central não respondeu nesta consulta. Nenhum valor foi presumido.")
    else:
        st.dataframe(ref, use_container_width=True, hide_index=True,
            column_config={"Fonte":st.column_config.LinkColumn("Banco Central")})
        st.caption("Selic meta (SGS 432): percentual ao ano. IPCA (SGS 433): variação mensal. Fontes oficiais, não intradiárias.")
    st.caption("A exibição de dados licenciados da Twelve Data só será ativada se houver chave no Render e autorização formal de redistribuição pública (MARKET_PUBLIC_DISPLAY_LICENSED=1). Não inclua chaves no GitHub. Histórico 1900–2026 permanece heurístico e isolado dos preços.")



# ---------- News and emergency monitoring (v8) ----------
NEWS_TTL_SECONDS = 600  # cache for ten minutes; actual updates depend on the source
SOURCE_LINKS = {
    "INMET — avisos": "https://avisos.inmet.gov.br/",
    "SIMGE — tempestades em MG": "https://simge.mg.gov.br/web/simge/alerta-de-tempestade-severa",
    "Boletim estadual de Defesa Civil": "https://www.mg.gov.br/servico/consultar-o-boletim-estadual-de-defesa-civil",
    "Defesa Civil MG — notícias": "https://www.mg.gov.br/defesacivil/noticias",
    "Prefeitura de Guarda-Mor": "https://www.guardamor.mg.gov.br/portal/noticias",
    "Agência Brasil — RSS": "https://agenciabrasil.ebc.com.br/feed/",
    "GDACS — alertas de desastres": "https://www.gdacs.org/",
    "NASA EONET": "https://eonet.gsfc.nasa.gov/",
    "Cadastro Defesa Civil — serviço federal": "https://www.gov.br/pt-br/servicos/solicitar-cadastro-para-recebimento-de-avisos-e-alertas-de-desastres",
}

RSS_LATEST = "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml"
RSS_POLITICS = "https://agenciabrasil.ebc.com.br/rss/politica/feed.xml"
RSS_INTERNATIONAL = "https://agenciabrasil.ebc.com.br/rss/internacional/feed.xml"
RSS_LOCAL = "https://www.guardamor.mg.gov.br/portal/rss"
RSS_GDACS = "https://www.gdacs.org/xml/rss.xml"


def news_now():
    return datetime.now(timezone.utc)


def news_local_time(iso_value):
    if not iso_value:
        return "Data não informada"
    try:
        dt = datetime.fromisoformat(str(iso_value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(iso_value)[:19]


def news_strip_html(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(value)).strip()[:350]


def news_dt(value):
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except Exception:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except Exception:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def clean_url(value):
    url = (value or "").strip()
    return url if url.startswith(("https://", "http://")) else ""


def news_item(title, link, published, source, category, summary="", kind="Notícia", extra=None):
    dt = news_dt(published)
    obj = {
        "titulo": news_strip_html(title),
        "url": clean_url(link),
        "data": dt.isoformat() if dt else None,
        "fonte": source,
        "categoria": category,
        "tipo_registro": kind,
        "resumo": news_strip_html(summary),
    }
    if extra:
        obj.update(extra)
    return obj


def parse_rss_xml(raw, source, category):
    """Supports RSS 2.0 and Atom; no dependence on feedparser."""
    root = ET.fromstring(raw)
    records = []
    items = root.findall(".//item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    for item in items[:75]:
        title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or ""
        link = item.findtext("link") or ""
        if not link:
            for a in item.findall("{http://www.w3.org/2005/Atom}link"):
                href = a.attrib.get("href")
                if href:
                    link = href
                    break
        published = (
            item.findtext("pubDate") or
            item.findtext("{http://www.w3.org/2005/Atom}published") or
            item.findtext("{http://www.w3.org/2005/Atom}updated") or
            item.findtext("{http://purl.org/dc/elements/1.1/}date")
        )
        summary = item.findtext("description") or item.findtext("{http://www.w3.org/2005/Atom}summary") or ""
        alert_level = item.findtext("{http://www.gdacs.org}alertlevel") or ""
        event_type = item.findtext("{http://www.gdacs.org}eventtype") or ""
        extra = {"nivel_gdacs": alert_level, "tipo_gdacs": event_type} if source == "GDACS" else None
        record = news_item(title, link, published, source, category, summary,
                           kind="Evento monitorado" if source == "GDACS" else "Notícia", extra=extra)
        if record["titulo"] and record["url"]:
            records.append(record)
    return records


@st.cache_data(ttl=NEWS_TTL_SECONDS, show_spinner=False)
def get_rss_news(url, source, category):
    checked = news_now().isoformat()
    if not REQUESTS_OK:
        return [], "Biblioteca requests não está instalada", checked
    try:
        response = requests.get(url, headers={"User-Agent": "InstabilidadeGlobalMonitor/1.0 (news monitoring)"}, timeout=(4, 10))
        response.raise_for_status()
        records = parse_rss_xml(response.content, source, category)
        if not records:
            return [], "A fonte respondeu sem registros legíveis", checked
        return records, "", checked
    except Exception as exc:
        return [], f"{type(exc).__name__}: {str(exc)[:110]}", checked


def google_news_url(query, international=False):
    base = "https://news.google.com/rss/search"
    params = {
        "q": query,
        "hl": "en-US" if international else "pt-BR",
        "gl": "US" if international else "BR",
        "ceid": "US:en" if international else "BR:pt",
    }
    return base + "?" + urlencode(params)


@st.cache_data(ttl=NEWS_TTL_SECONDS, show_spinner=False)
def get_gdelt_conflicts(days):
    checked = news_now().isoformat()
    if not REQUESTS_OK:
        return [], "Biblioteca requests não está instalada", checked
    query = '("armed conflict" OR "airstrike" OR "ceasefire" OR "missile strike")'
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "sort": "DateDesc",
        "maxrecords": 35,
        "timespan": f"{days}d",
    }
    try:
        response = requests.get("https://api.gdeltproject.org/api/v2/doc/doc", params=params,
                                headers={"User-Agent": "InstabilidadeGlobalMonitor/1.0"}, timeout=(4, 12))
        response.raise_for_status()
        payload = response.json()
        records = []
        for article in payload.get("articles", []):
            raw_date = article.get("seendate", "")
            # GDELT seendate format YYYYMMDDTHHMMSSZ
            try:
                dt = datetime.strptime(raw_date, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
                when = dt.isoformat()
            except Exception:
                when = None
            records.append(news_item(article.get("title", ""), article.get("url", ""), when,
                                     article.get("domain", "GDELT"), "Conflitos",
                                     "Notícia encontrada no índice GDELT; não é confirmação de ocorrência."))
        return [r for r in records if r["url"] and r["titulo"]], "", checked
    except Exception as exc:
        return [], f"{type(exc).__name__}: {str(exc)[:110]}", checked


@st.cache_data(ttl=NEWS_TTL_SECONDS, show_spinner=False)
def get_eonet_events(days):
    checked = news_now().isoformat()
    if not REQUESTS_OK:
        return [], "Biblioteca requests não está instalada", checked
    try:
        url = "https://eonet.gsfc.nasa.gov/api/v3/events"
        response = requests.get(url, params={"days": days, "status": "all", "limit": 150}, timeout=(4, 12))
        response.raise_for_status()
        events = response.json().get("events", [])
        records = []
        for event in events:
            cats = [c.get("title", "") for c in event.get("categories", [])]
            geometries = event.get("geometry", []) or []
            geo = geometries[-1] if geometries else {}
            coords = geo.get("coordinates", [])
            lat, lon = None, None
            if geo.get("type") == "Point" and isinstance(coords, list) and len(coords) >= 2:
                lon, lat = coords[0], coords[1]
            # Exclude volcanoes/earthquakes in this weather-and-environment view
            cat_text = " ".join(cats).lower()
            if not any(tag in cat_text for tag in ["storm", "flood", "wildfire", "drought", "dust", "snow", "sea and lake", "temperature"]):
                continue
            srcs = event.get("sources", []) or []
            source_url = clean_url(srcs[0].get("url", "")) if srcs else ""
            records.append(news_item(event.get("title", ""), source_url or "https://eonet.gsfc.nasa.gov/",
                                     geo.get("date"), "NASA EONET", "Eventos naturais", ", ".join(cats),
                                     kind="Evento monitorado", extra={"latitude": lat, "longitude": lon,
                                                                       "categorias_nasa": ", ".join(cats),
                                                                       "encerrado": bool(event.get("closed"))}))
        return records, "", checked
    except Exception as exc:
        return [], f"{type(exc).__name__}: {str(exc)[:110]}", checked


def filter_news_items(records, days=None, keyword="", limit=60):
    cutoff = news_now() - timedelta(days=days) if days else None
    keyword = (keyword or "").casefold().strip()
    cleaned, seen = [], set()
    for row in records:
        if not row.get("url") or not row.get("titulo"):
            continue
        key = re.sub(r"\W+", "", row["titulo"].casefold())[:100]
        if key in seen:
            continue
        dt = news_dt(row.get("data"))
        if cutoff and dt and dt < cutoff:
            continue
        if keyword and keyword not in (row["titulo"] + " " + row.get("resumo", "")).casefold():
            continue
        seen.add(key)
        cleaned.append(row)
    cleaned.sort(key=lambda r: r.get("data") or "", reverse=True)
    return cleaned[:limit]


def show_source_errors(errors):
    for name, error, checked in errors:
        if error:
            st.warning(f"{name}: falha na consulta ({error}). Não é possível determinar a situação atual por essa fonte.")


def show_news_cards(records, limit=20):
    if not records:
        st.info("Nenhuma notícia compatível encontrada nas fontes consultadas. Isso não significa ausência de eventos.")
        return
    st.caption(f"{len(records)} registros encontrados nos filtros selecionados. O horário indica publicação/indexação, quando disponível.")
    for idx, item in enumerate(records[:limit]):
        with st.container(border=True):
            st.markdown("**" + item["titulo"].replace("*", "\\*") + "**")
            st.caption(f"{item.get('tipo_registro', 'Notícia')} · {item['fonte']} · {news_local_time(item.get('data'))} (Brasília)")
            if item.get("resumo"):
                st.write(item["resumo"])
            if item.get("nivel_gdacs"):
                st.caption(f"Classificação GDACS reportada: {item['nivel_gdacs']} | Tipo: {item.get('tipo_gdacs','N/D')}")
            st.link_button("Abrir fonte original", item["url"])


def export_news_rows(records, filename):
    if records:
        cols = ["titulo", "fonte", "data", "categoria", "tipo_registro", "url", "resumo"]
        csv = pd.DataFrame(records).reindex(columns=cols).to_csv(index=False).encode("utf-8-sig")
        st.download_button("Exportar resultados CSV", csv, file_name=filename, mime="text/csv", key=f"export_{filename}")


def report_news_status(sources):
    for source, checked in sources:
        if checked:
            st.caption(f"Consulta a {source}: {news_local_time(checked)} (Brasília) · atualização em cache por até 10 minutos")


def render_monitoring_panel():
    st.subheader("Centro de Monitoramento — notícias, conflitos, clima e Defesa Civil")
    st.caption("Monitoramento sob demanda com cache de 10 min. Não é streaming contínuo: cada fonte atualiza no seu próprio ritmo.")
    if not REQUESTS_OK:
        st.error("Instale a dependência: python -m pip install requests")
        return
    category = st.radio("Canal", ["Notícias gerais", "Conflitos", "Eventos climáticos", "Governos", "Defesa Civil — Guarda-Mor"], horizontal=True)
    b, c = st.columns([1, 1])
    with b:
        filter_days = st.selectbox("Período das notícias", [2, 7, 30], index=1)
    with c:
        if st.button("Atualizar fontes agora", key="update_news", use_container_width=True):
            get_rss_news.clear()
            get_gdelt_conflicts.clear()
            get_eonet_events.clear()
            st.rerun()
    keyword = st.text_input("Filtrar resultados pelo título ou resumo (opcional)", placeholder="Ex.: inflação, Ucrânia, tempestade, Guarda-Mor")
    items, errors, source_times = [], [], []
    
    def append_rss(url, source, kind):
        rows, err, checked = get_rss_news(url, source, kind)
        items.extend(rows)
        errors.append((source, err, checked))
        source_times.append((source, checked))

    if category == "Notícias gerais":
        append_rss(RSS_LATEST, "Agência Brasil", "Notícias")
        append_rss(google_news_url('notícias internacionais economia geopolítica when:2d'), "Google Notícias (índice)", "Notícias")
        st.info("Notícias indexadas podem conter versões não verificadas de acontecimentos. Consulte a fonte original.")

    elif category == "Conflitos":
        gdelt_rows, err, checked = get_gdelt_conflicts(min(filter_days, 30))
        items.extend(gdelt_rows)
        errors.append(("GDELT", err, checked))
        source_times.append(("GDELT", checked))
        append_rss(google_news_url('(war OR conflict OR ceasefire OR airstrike) when:2d', international=True), "Google Notícias (índice)", "Conflitos")
        st.info("Estes são relatos jornalísticos sobre conflitos, não uma contagem validada de batalhas, vítimas ou guerras. Para dados de ocorrências, é necessária uma base validada como ACLED/UCDP.")

    elif category == "Eventos climáticos":
        append_rss(RSS_GDACS, "GDACS", "Desastres")
        # GDACS also includes earthquakes and tsunamis: weather-focused selection
        items = [r for r in items if r.get("fonte") != "GDACS" or
                 r.get("tipo_gdacs", "").upper() in {"TC", "FL", "DR", "WF"} or
                 (not r.get("tipo_gdacs") and any(w in r["titulo"].lower() for w in
                  ["flood", "storm", "cyclone", "fire", "drought", "inunda", "tempestade"]))]
        nasa_rows, err, checked = get_eonet_events(filter_days)
        items.extend(nasa_rows)
        errors.append(("NASA EONET", err, checked))
        source_times.append(("NASA EONET", checked))
        st.info("GDACS e NASA EONET monitoram eventos naturais. A ausência de registros não equivale a uma previsão meteorológica favorável.")
        geo_records = [r for r in nasa_rows if isinstance(r.get("latitude"), (int, float)) and isinstance(r.get("longitude"), (int, float))]
        if geo_records:
            try:
                st.map(pd.DataFrame(geo_records).rename(columns={"latitude": "lat", "longitude": "lon"})[["lat", "lon"]].dropna())
            except Exception:
                st.caption("Localizações de eventos disponíveis na tabela, mas mapa indisponível.")
        st.link_button("Consultar avisos meteorológicos oficiais (Brasil)", SOURCE_LINKS["INMET — avisos"])

    elif category == "Governos":
        append_rss(RSS_POLITICS, "Agência Brasil — Política", "Governo federal")
        append_rss(RSS_LOCAL, "Prefeitura de Guarda-Mor (oficial)", "Governo municipal")
        append_rss(google_news_url('site:gov.br (decreto OR governo OR ministério OR política) when:7d'), "Google Notícias — órgãos federais (índice)", "Governo federal")
        append_rss(google_news_url('(government OR regulation OR cabinet OR parliament) when:2d', international=True), "Google Notícias — governos mundiais (índice)", "Governos internacionais")
        st.caption("Comunicados governamentais e notícias da imprensa são apresentados com suas fontes identificadas, sem avaliação política de dirigentes.")

    elif category == "Defesa Civil — Guarda-Mor":
        st.markdown("#### Guarda-Mor/MG e Noroeste de Minas")
        st.warning("Este painel não substitui alertas oficiais enviados pela Defesa Civil. Uma notícia ou menção à cidade não comprova que exista alerta ativo.")
        left, right = st.columns(2)
        with left:
            st.link_button("INMET — verificar avisos para Minas Gerais", SOURCE_LINKS["INMET — avisos"], use_container_width=True)
            st.link_button("SIMGE — alertas de tempestades em MG", SOURCE_LINKS["SIMGE — tempestades em MG"], use_container_width=True)
        with right:
            st.link_button("Boletim da Defesa Civil de MG", SOURCE_LINKS["Boletim estadual de Defesa Civil"], use_container_width=True)
            st.link_button("Notícias da Prefeitura de Guarda-Mor", SOURCE_LINKS["Prefeitura de Guarda-Mor"], use_container_width=True)
        st.caption("Alertas por SMS: envie o CEP de interesse para 40199. Emergências: Defesa Civil 199 ou Bombeiros 193.")
        append_rss(RSS_LOCAL, "Prefeitura de Guarda-Mor (oficial)", "Guarda-Mor")
        items = [r for r in items if any(w in (r["titulo"] + " " + r.get("resumo", "")).casefold() for w in
                                     ["defesa civil", "chuva", "enchente", "alagamento", "incêndio", "tempestade", "seca", "queimada", "vento forte", "ponte", "drenagem"])]
        append_rss(google_news_url('"Guarda-Mor" ("defesa civil" OR chuva OR tempestade OR alagamento OR incêndio) when:30d'),
                   "Google Notícias — Guarda-Mor (índice)", "Defesa Civil local")
        append_rss(google_news_url('site:mg.gov.br/defesacivil ("Guarda-Mor" OR "Noroeste de Minas") when:30d'),
                   "Google Notícias — Defesa Civil MG (índice)", "Defesa Civil estadual")
        st.caption("As publicações da Prefeitura são oficiais; notícias recuperadas por buscador podem ser de terceiros ou estar atrasadas. O portal do INMET e o SIMGE devem ser consultados para avisos vigentes.")

    filtered = filter_news_items(items, days=filter_days if category not in ("Defesa Civil — Guarda-Mor", "Eventos climáticos") else 30,
                                 keyword=keyword, limit=100)
    if not filtered and items:
        st.info("Há registros na fonte, mas nenhum dentro do período/filtro escolhido. Amplie o período se necessário.")
    show_source_errors(errors)
    st.metric("Registros no filtro", len(filtered))
    report_news_status(source_times)
    show_news_cards(filtered, limit=25)
    export_news_rows(filtered, "monitoramento_global.csv")
    with st.expander("Fontes, atualização e limitações"):
        for name, link in SOURCE_LINKS.items():
            st.markdown(f"- [{name}]({link})")
        st.caption("Leituras de RSS, GDELT, GDACS e NASA dependem da disponibilidade dos serviços. As notícias não alteram automaticamente o índice histórico nem produzem alertas oficiais.")

# ---------- UI ----------

# ---------- Identidade visual institucional (inspirada no Padrão Digital de Governo) ----------
def apply_institutional_style():
    st.markdown("""<style>
    :root { --oi-blue:#1351B4; --oi-deep:#071D41; --oi-bg:#F5F7FA; --oi-ink:#1D2D44; }
    .stApp {background:var(--oi-bg); color:var(--oi-ink);}
    [data-testid="stHeader"] {background:rgba(245,247,250,.96);}
    [data-testid="stSidebar"] {background:#EBF1FA; border-right:1px solid #CDD7E5;}
    [data-testid="stSidebar"] h2 {color:var(--oi-deep);}
    .block-container {padding-top:1.4rem; max-width:1500px;}
    .oi-header {background:#fff; border-top:5px solid var(--oi-blue); border-bottom:1px solid #CCD5E4;
       padding:1.45rem 1.65rem; border-radius:0 0 12px 12px; margin-bottom:1.5rem;}
    .oi-header .oi-kicker {font-size:.85rem; text-transform:uppercase; letter-spacing:.08em;
       color:#24539A; font-weight:700; margin-bottom:.6rem;}
    .oi-header h1 {font-size:clamp(1.5rem,2.5vw,2.45rem); line-height:1.2;
       color:var(--oi-deep); margin:0 0 .6rem 0;}
    .oi-header p {font-size:1rem; line-height:1.6; color:#40546E; margin:0; max-width:1000px;}
    [data-testid="stMetric"] {background:#fff; border:1px solid #D9E1EB; padding:1rem; border-radius:10px;}
    [data-testid="stMetricLabel"] {color:#40546E;}
    [data-baseweb="tab"] {font-weight:600; color:#163864;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-color:#D9E1EB;}
    a:focus-visible, button:focus-visible, [role="tab"]:focus-visible,
    input:focus-visible {outline:3px solid #E0A800 !important; outline-offset:2px;}
    .oi-footer {border-top:1px solid #CCD5E4; margin-top:1.5rem; padding-top:1rem;
       color:#40546E; font-size:.86rem; line-height:1.5;}
    @media (max-width:700px) {.oi-header{padding:1.1rem}.block-container{padding-top:.7rem}}
    </style>""", unsafe_allow_html=True)


def show_institutional_header():
    # Sem brasão, bandeira oficial, domínio gov.br ou alegação de vínculo governamental.
    st.markdown("""
    <header class="oi-header" role="banner">
      <div class="oi-kicker">Observatório independente · Dados públicos</div>
      <h1>Observatório de Instabilidade Global</h1>
      <p>Painel analítico de indicadores históricos, mercados, notícias e eventos climáticos,
         com monitoramento público de Guarda-Mor e Minas Gerais.</p>
    </header>
    """, unsafe_allow_html=True)


apply_institutional_style()
show_institutional_header()
st.caption("Histórico · Previsões · Padrões · Cenários · Mercado observado · Notícias · Defesa Civil")
st.info("**Aviso de transparência:** a série histórica 1900–2026 é **heurística e ilustrativa**, não oficial. Os scores de risco/retorno são hipóteses do modelo, não previsões validadas nem recomendações de investimento. Este é um painel independente e **não substitui alertas oficiais da Defesa Civil**.")

with st.sidebar:
    st.header("Configurações")
    uploaded_file = st.file_uploader("Enviar CSV", type=["csv"])
    use_uploaded = uploaded_file is not None

    st.subheader("Pesos do índice")
    default_weights = {"war": 0.20, "climate": 0.15, "economy": 0.15, "politics": 0.10, "science": 0.10, "demography": 0.15, "health": 0.15}
    weights = {key: st.slider(LABELS[key], 0.0, 1.0, float(default_weights[key]), 0.01) for key in DIMENSIONS}

    st.subheader("Controles gerais")
    show_original = st.toggle("Mostrar índice original", value=True)
    highlight_orbital = st.toggle("Destacar anos orbitais", value=True)
    cp_sensitivity = st.slider("Sensibilidade de ruptura", 0.5, 3.0, 1.0, 0.25)
    rolling_corr_window = st.slider("Janela correlação móvel", 5, 30, 10, 1)

    st.subheader("Previsões")
    horizon = st.slider("Horizonte (anos)", 3, 30, 10, 1)
    ma_window = st.slider("Janela média móvel", 2, 10, 3, 1)
    exp_alpha = st.slider("Alpha suavização", 0.05, 0.95, 0.35, 0.05)
    poly_degree = st.slider("Grau polinomial", 2, 4, 2, 1)

    st.subheader("Cenários")
    scenario_mode = st.selectbox("Modo do cenário", ["Mudança permanente", "Choque único", "Escalada gradual"], index=0)
    scenario_horizon = st.slider("Horizonte do cenário", 1, 20, 8, 1)

    st.subheader("Mercado")
    investor_profile = st.selectbox("Perfil de alocação", ["Conservador", "Balanceado", "Agressivo"], index=1)
    market_scope = st.selectbox("Universo setorial", ["ETFs", "Ações EUA", "Ações Brasil"], index=0)
    macro_period = st.selectbox("Período macro", ["6mo", "1y", "2y", "5y"], index=2)

df = pd.read_csv(uploaded_file) if use_uploaded else load_default_data()
df = ensure_columns(df)
df = compute_index(df, weights)

min_year, max_year = int(df["year"].min()), int(df["year"].max())
year_range = st.slider("Intervalo de anos", min_year, max_year, (min_year, max_year))

view = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])].copy()
view["zone"] = view["global_index_calc"].apply(classify_zone)
view = assign_regimes(view)

latest = view.iloc[-1]
peak = view.loc[view["global_index_calc"].idxmax()]
orbital_years = int(view["orbital"].fillna(0).gt(0).sum())

years = view["year"].to_numpy()
values = view["global_index_calc"].to_numpy(dtype=float)

forecast_frames = [
    clamp_forecast(moving_average_forecast(years, values, horizon, ma_window)),
    clamp_forecast(linear_regression_forecast(years, values, horizon)),
    clamp_forecast(polynomial_forecast(years, values, horizon, poly_degree)),
    clamp_forecast(exponential_smoothing_forecast(years, values, horizon, exp_alpha)),
]
forecast_df = pd.concat([f for f in forecast_frames if not f.empty], ignore_index=True) if any(not f.empty for f in forecast_frames) else pd.DataFrame(columns=["year", "forecast", "model"])
ensemble_df = pd.DataFrame()
if not forecast_df.empty:
    ensemble_df = forecast_df.groupby("year", as_index=False)["forecast"].mean()
    ensemble_df["zone"] = ensemble_df["forecast"].apply(classify_zone)

scenario_deltas = {}
scenario_cols = st.columns(4)
for i, dim in enumerate(DIMENSIONS):
    with scenario_cols[i % 4]:
        scenario_deltas[dim] = st.slider(f"Cenário {LABELS[dim]}", -3.0, 3.0, 0.0, 0.5, key=f"scenario_{dim}")
scenario_df = build_scenario_df(latest, scenario_deltas, scenario_horizon, weights, scenario_mode)

change_points = detect_change_points(view, cp_sensitivity)
cycle_df = detect_dominant_cycle(values)
driver_df = get_driver_table(view)
corr_df = view[DIMENSIONS].corr().rename(index=LABELS, columns=LABELS)

sector_df = calculate_sector_rotation(latest)
portfolio_df = suggest_portfolio(sector_df, investor_profile)

market_map_df = get_market_table(sector_df, market_scope)
market_tickers = market_map_df["Ticker"].dropna().unique().tolist()
sector_prices = download_prices(market_tickers, period="2y")
sector_stats = perf_stats_from_prices(sector_prices)
market_rank = blend_market_and_model(market_map_df, sector_stats)

macro_map = build_macro_ticker_table()
macro_prices = download_prices(macro_map["Ticker"].tolist(), period=macro_period)
macro_stats = perf_stats_from_prices(macro_prices)
macro_rank = build_macro_rank(macro_stats, macro_map)
signal_df = build_signal_table(macro_rank)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Índice atual", f"{latest['global_index_calc']:.2f}", latest["zone"])
m2.metric("Pico no período", f"{peak['global_index_calc']:.2f}", f"Ano {int(peak['year'])}")
m3.metric("Maior score setorial*", sector_df.iloc[0]["Setor"])
m4.metric("Maior score macro*", macro_rank.iloc[0]["Ativo"] if not macro_rank.empty else "N/D")

tabs = st.tabs([
    "Visão geral",
    "Previsões",
    "Cenários",
    "Padrões",
    "Rotação setorial",
    "Mercado real",
    "Macro global",
    "Sinais",
    "Dados e exportação",
    "Monitoramento ao vivo",
    "Mercado observado",
    "Sobre e transparência",
])

with tabs[0]:
    fig = go.Figure()
    if show_original and view["global_index"].notna().any():
        fig.add_trace(go.Scatter(x=view["year"], y=view["global_index"], mode="lines+markers", name="Índice original"))
    fig.add_trace(go.Scatter(x=view["year"], y=view["global_index_calc"], mode="lines+markers", name="Índice calculado"))
    if highlight_orbital:
        orbital_points = view[view["orbital"].fillna(0) > 0]
        if not orbital_points.empty:
            fig.add_trace(go.Scatter(x=orbital_points["year"], y=orbital_points["global_index_calc"], mode="markers", name="Orbital", marker=dict(size=11, symbol="diamond")))
    if not change_points.empty:
        fig.add_trace(go.Scatter(x=change_points["year"], y=change_points["global_index_calc"], mode="markers", name="Rupturas", marker=dict(size=11, symbol="x")))
    if not ensemble_df.empty:
        fig.add_trace(go.Scatter(x=ensemble_df["year"], y=ensemble_df["forecast"], mode="lines+markers", name="Ensemble", line=dict(dash="dash")))
    fig.update_layout(title="Índice global de instabilidade", xaxis_title="Ano", yaxis_title="Índice", height=480)
    st.plotly_chart(fig, use_container_width=True)

    peak_table = view.sort_values("global_index_calc", ascending=False)[["year", "global_index_calc", "zone", "regime"]].head(10)
    st.dataframe(peak_table.rename(columns={"year": "Ano", "global_index_calc": "Índice", "zone": "Zona", "regime": "Regime"}), use_container_width=True, hide_index=True)

with tabs[1]:
    if forecast_df.empty:
        st.warning("Sem dados suficientes para previsões.")
    else:
        pf = go.Figure()
        pf.add_trace(go.Scatter(x=view["year"], y=view["global_index_calc"], mode="lines+markers", name="Histórico"))
        for model_name, sub in forecast_df.groupby("model"):
            pf.add_trace(go.Scatter(x=sub["year"], y=sub["forecast"], mode="lines+markers", name=model_name))
        if not ensemble_df.empty:
            pf.add_trace(go.Scatter(x=ensemble_df["year"], y=ensemble_df["forecast"], mode="lines+markers", name="Ensemble", line=dict(width=4, dash="dash")))
        pf.update_layout(title="Modelos de previsão", xaxis_title="Ano", yaxis_title="Índice", height=500)
        st.plotly_chart(pf, use_container_width=True)
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)

with tabs[2]:
    sf = go.Figure()
    sf.add_trace(go.Scatter(x=view["year"], y=view["global_index_calc"], mode="lines+markers", name="Histórico"))
    if not scenario_df.empty:
        sf.add_trace(go.Scatter(x=scenario_df["year"], y=scenario_df["scenario_index"], mode="lines+markers", name="Cenário", line=dict(width=4)))
    sf.update_layout(title="Simulação de cenário", xaxis_title="Ano", yaxis_title="Índice", height=500)
    st.plotly_chart(sf, use_container_width=True)
    if not scenario_df.empty:
        st.dataframe(scenario_df, use_container_width=True, hide_index=True)

with tabs[3]:
    c1, c2, c3 = st.columns(3)
    c1.metric("Ciclo dominante", "N/D" if cycle_df.empty else f"{cycle_df.iloc[0]['period_years']:.1f} anos")
    c2.metric("Rupturas", len(change_points))
    c3.metric("Regime atual", str(view.iloc[-1]["regime"]))

    if not cycle_df.empty:
        st.plotly_chart(px.bar(cycle_df.head(8), x="period_years", y="amplitude", title="Ciclos dominantes por FFT"), use_container_width=True)
    if not change_points.empty:
        cp_fig = go.Figure()
        cp_fig.add_trace(go.Scatter(x=view["year"], y=view["global_index_calc"], mode="lines+markers", name="Índice"))
        cp_fig.add_trace(go.Scatter(x=change_points["year"], y=change_points["global_index_calc"], mode="markers", name="Rupturas", marker=dict(size=12, symbol="x")))
        cp_fig.update_layout(title="Rupturas detectadas", xaxis_title="Ano", yaxis_title="Índice", height=420)
        st.plotly_chart(cp_fig, use_container_width=True)

    st.plotly_chart(px.imshow(corr_df, text_auto=".2f", aspect="auto", title="Matriz de correlação"), use_container_width=True)

    rolling_rows = []
    for dim in DIMENSIONS:
        roll = view[dim].rolling(rolling_corr_window).corr(view["global_index_calc"])
        rolling_rows.append(pd.DataFrame({"year": view["year"], "dimension": LABELS[dim], "corr": roll}))
    rolling_df = pd.concat(rolling_rows, ignore_index=True).dropna()
    if not rolling_df.empty:
        st.plotly_chart(px.line(rolling_df, x="year", y="corr", color="dimension", title=f"Correlação móvel com o índice (janela {rolling_corr_window})"), use_container_width=True)

    st.dataframe(driver_df.rename(columns={"year": "Ano", "driver": "Driver dominante", "driver_value": "Valor"}), use_container_width=True, hide_index=True)

with tabs[4]:
    st.plotly_chart(px.scatter(sector_df, x="Risco_estimado", y="Retorno_potencial", size="Eficiência", color="Estilo", text="Setor", title="Mapa risco x retorno dos setores"), use_container_width=True)
    st.dataframe(sector_df, use_container_width=True, hide_index=True)
    st.plotly_chart(px.pie(portfolio_df.head(8), names="Setor", values="Alocação_%", title=f"Carteira sugerida — perfil {investor_profile.lower()}"), use_container_width=True)
    st.dataframe(portfolio_df, use_container_width=True, hide_index=True)

with tabs[5]:
    st.subheader(f"Mercado real — {market_scope}")
    if not YF_OK:
        st.error("Instale: pip install yfinance")
    elif market_rank.empty:
        st.warning("Sem dados de mercado real no momento.")
    else:
        st.dataframe(market_rank[["Setor", "Ticker", "Ret_1M", "Ret_3M", "Ret_6M", "Ret_12M", "Vol_3M", "Max_Drawdown", "Score_operacional"]], use_container_width=True, hide_index=True)
        market_rank_plot = market_rank.copy()
        market_rank_plot["BubbleSize"] = market_rank_plot["Score_operacional"].fillna(0).clip(lower=0).abs() + 0.01
        st.plotly_chart(
            px.scatter(
                market_rank_plot,
                x="Vol_3M",
                y="Ret_6M",
                size="BubbleSize",
                color="Setor",
                hover_name="Ticker",
                hover_data=["Score_operacional"],
                title="Retorno 6M x volatilidade 3M",
            ),
            use_container_width=True,
        )
        chosen = st.selectbox("Ativo setorial", options=market_rank["Ticker"].tolist(), key="setorial_asset")
        if chosen in sector_prices.columns:
            price_fig = go.Figure()
            price_fig.add_trace(go.Scatter(x=sector_prices.index, y=sector_prices[chosen], mode="lines", name=chosen))
            price_fig.update_layout(title=f"Preço ajustado — {chosen}", xaxis_title="Data", yaxis_title="Preço", height=420)
            st.plotly_chart(price_fig, use_container_width=True)

with tabs[6]:
    st.subheader("Macro global")
    if not YF_OK:
        st.error("Instale: pip install yfinance")
    elif macro_rank.empty:
        st.warning("Sem dados macro no momento.")
    else:
        st.dataframe(macro_rank[["Grupo", "Ativo", "Ticker", "Ret_1M", "Ret_3M", "Ret_6M", "Ret_12M", "Vol_3M", "Max_Drawdown", "Score_macro"]], use_container_width=True, hide_index=True)
        group_choice = st.selectbox("Grupo macro", options=list(MACRO_UNIVERSE.keys()), key="macro_group")
        group_df = macro_rank[macro_rank["Grupo"] == group_choice]
        if not group_df.empty:
            st.plotly_chart(px.bar(group_df, x="Ativo", y="Score_macro", color="Ativo", title=f"Ranking — {group_choice}"), use_container_width=True)
            group_df_plot = group_df.copy()
            group_df_plot["BubbleSize"] = group_df_plot["Score_macro"].fillna(0).clip(lower=0).abs() + 0.01
            st.plotly_chart(
                px.scatter(
                    group_df_plot,
                    x="Vol_3M",
                    y="Ret_6M",
                    size="BubbleSize",
                    color="Ativo",
                    text="Ativo",
                    hover_data=["Score_macro"],
                    title=f"{group_choice}: retorno 6M x volatilidade 3M",
                ),
                use_container_width=True,
            )
            chosen_macro = st.selectbox("Ativo macro", options=group_df["Ticker"].tolist(), key="macro_asset")
            if chosen_macro in macro_prices.columns:
                mf = go.Figure()
                mf.add_trace(go.Scatter(x=macro_prices.index, y=macro_prices[chosen_macro], mode="lines", name=chosen_macro))
                mf.update_layout(title=f"Série — {chosen_macro}", xaxis_title="Data", yaxis_title="Valor", height=420)
                st.plotly_chart(mf, use_container_width=True)

with tabs[7]:
    if signal_df.empty:
        st.warning("Sem dados suficientes para sinais.")
    else:
        st.dataframe(signal_df, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(signal_df, x="Sinal", y="Score", color="Leitura", title="Sinais macro operacionais"), use_container_width=True)
        st.info("Leitura automática: " + macro_summary_text(signal_df))

with tabs[8]:
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("Baixar CSV histórico", view.to_csv(index=False).encode("utf-8"), file_name=f"historico_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
    if not forecast_df.empty:
        st.download_button("Baixar CSV previsões", forecast_df.to_csv(index=False).encode("utf-8"), file_name=f"forecast_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
    if not scenario_df.empty:
        st.download_button("Baixar CSV cenários", scenario_df.to_csv(index=False).encode("utf-8"), file_name=f"scenario_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
    st.download_button("Baixar CSV setores", sector_df.to_csv(index=False).encode("utf-8"), file_name=f"setores_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
    st.download_button("Baixar CSV carteira", portfolio_df.to_csv(index=False).encode("utf-8"), file_name=f"carteira_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
    if not market_rank.empty:
        st.download_button("Baixar CSV mercado real", market_rank.to_csv(index=False).encode("utf-8"), file_name=f"mercado_real_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
    if not macro_rank.empty:
        st.download_button("Baixar CSV macro global", macro_rank.to_csv(index=False).encode("utf-8"), file_name=f"macro_global_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
    if not signal_df.empty:
        st.download_button("Baixar CSV sinais", signal_df.to_csv(index=False).encode("utf-8"), file_name=f"sinais_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

st.markdown("---")
st.markdown("Arquivo único consolidado. Para mercado real e macro global, instale: `pip install yfinance`.")


# ---------- Real-time monitoring page ----------
with tabs[9]:
    render_monitoring_panel()

with tabs[10]:
    live_market_panel()


with tabs[11]:
    st.subheader("Sobre o observatório")
    st.markdown("""
    **Natureza:** projeto independente de análise e visualização de dados públicos.
    Não representa nem substitui governos, órgãos de Defesa Civil, instituições financeiras
    ou serviços de emergência. A aparência visual foi inspirada em princípios públicos do
    [Padrão Digital de Governo](https://www.gov.br/ds), sem certificação de conformidade.

    **Cobertura:** indicadores históricos heurísticos de 1900–2026, cenários analíticos,
    dados financeiros de terceiros e links para publicações de órgãos oficiais.

    **Atualização:** os dados financeiros são buscados sob demanda com cache; notícias e
    eventos são consultados sob demanda, em geral com cache de até dez minutos.
    Ausência de registro no painel não comprova ausência de emergência ou risco.

    **Metodologia:** índices de 0 a 5 e pesos são definidos como parâmetros de estudo,
    sem validação preditiva. Atribuição de causa, antecipação de catástrofes e previsão
    de retorno não são conclusões sustentadas por estes indicadores.

    **Privacidade:** o app não solicita dados pessoais para uso público. Serviços
    externos de cotação e notícias recebem consultas HTTP do servidor hospedado.
    Para governança formal, consultar `POLITICA_DE_DADOS.md`, `ACESSIBILIDADE.md`
    e `README.md` do repositório.
    """)
    st.markdown("**Fontes de referência e verificação:**")
    for name, url in SOURCE_LINKS.items():
        st.markdown(f"- [{name}]({url})")
    st.caption("* Os scores e rankings são construções experimentais sem calibração estatística para investimento.")

st.markdown("""<footer class="oi-footer">
  Observatório de Instabilidade Global · Projeto independente ·
  Dados de terceiros sujeitos a atraso e indisponibilidade ·
  Em emergência, utilize os canais oficiais competentes.
</footer>""", unsafe_allow_html=True)