import streamlit as st
from utils.api import health
from utils.data import load_housing

st.set_page_config(page_title="ValoRe", layout="wide")

# THeader + intro
st.title("🏠 ValoRe — House Price Intelligence")
st.caption("Real-time prediction platform for King County, WA · ULiège INFO9023")

st.markdown(
    "**ValoRe** is an MLOps platform built for INFO9023. It serves an XGBoost model "
    "trained on **21,613 King County house sales (May 2014 – May 2015)**, from Kaggle Housing Price Dataset (https://www.kaggle.com/datasets/sukhmandeepsinghbrar/housing-price-dataset/data), and exposes it "
    "through a Cloud Run fastAPI. Use the sidebar below to estimate prices, explore the market, "
    "and inspect the model."
)

st.divider()

# API health badge
try:
    h = health()
    api_ok = True
except Exception:
    h = None
    api_ok = False

col_status, col_model = st.columns([1, 2])

with col_status:
    if not api_ok:
        st.error("API unreachable", icon="🔴")
    elif h.get("model_loaded"):
        st.success("API online · model loaded", icon="✅")
    else:
        st.warning("API online · model not loaded", icon="⚠️")

with col_model:
    if api_ok:
        st.caption(
            f"Model: **{h.get('model_display_name', '—')}** · "
            f"source: {h.get('model_source', '—')}"
        )
    else:
        st.caption("Could not reach the prediction API.")

st.divider()

# Dataset KPI strip
st.subheader("Dataset overview")

with st.spinner("Loading dataset stats…"):
    try:
        df = load_housing()
        avg_sqm = (df["sqft_living"] * 0.092903).mean()
        latest_date = df["date"].max()
        latest_str = (
            f"{latest_date[:4]}-{latest_date[4:6]}-{latest_date[6:8]}"
            if isinstance(latest_date, str) and len(latest_date) >= 8
            else "—"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total records", f"{len(df):,}")
        c2.metric("Median price", f"${df['price'].median():,.0f}")
        c3.metric("Avg living area", f"{avg_sqm:,.0f} sqm")
        c4.metric("Latest sale", latest_str)
    except Exception as e:
        st.info(f"Dataset stats unavailable: {e}")

st.divider()

# Clickable navigation cards
st.subheader("Explore")

c1, c2, c3 = st.columns(3)

with c1:
    st.page_link(
        "pages/1_Estimate_Price.py",
        label="**Estimate Price**",
        icon="💰",
        use_container_width=True,
    )
    st.caption(
        "Fill in house details and get a live price prediction from the deployed model."
    )

with c2:
    st.page_link(
        "pages/2_Explore_Market.py",
        label="**Explore Market**",
        icon="🗺️",
        use_container_width=True,
    )
    st.caption(
        "Interactive map and charts of the King County housing market, loaded from BigQuery."
    )

with c3:
    st.page_link(
        "pages/3_Model_Insights.py",
        label="**Model Insights**",
        icon="📊",
        use_container_width=True,
    )
    st.caption("Model versions and training story from the Vertex AI Model Registry.")
