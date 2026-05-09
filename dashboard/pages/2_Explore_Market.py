import plotly.express as px
import streamlit as st
from utils.data import load_housing

st.set_page_config(page_title="Explore Market · ValoRe", layout="wide")

st.title("Explore Market")
st.caption("King County housing market - loaded live from BigQuery.")

# Load dataset
with st.spinner("Loading dataset from BigQuery…"):
    try:
        df = load_housing()
    except Exception as e:
        st.error(f"Could not load data from BigQuery: {e}")
        st.stop()

# Sidebar filter panel
with st.sidebar:
    st.header("Filters")

    price_min = int(df["price"].min())
    price_max = int(df["price"].max())
    price_range = st.slider(
        "Price range (USD)",
        min_value=price_min,
        max_value=price_max,
        value=(75_000, 2_000_000),
        step=25_000,
        format="$%d",
    )

    grade_range = st.select_slider(
        "Grade",
        options=list(range(1, 14)),
        value=(4, 12),
    )

    yr_min = int(df["yr_built"].min())
    yr_max = int(df["yr_built"].max())
    yr_range = st.slider(
        "Year built",
        min_value=yr_min,
        max_value=yr_max,
        value=(1950, yr_max),
        step=1,
    )

    waterfront_opt = st.radio(
        "Waterfront",
        ["All", "Waterfront only", "Non-waterfront"],
        index=0,
    )

# Apply filters
filt = (
    (df["price"] >= price_range[0])
    & (df["price"] <= price_range[1])
    & (df["grade"] >= grade_range[0])
    & (df["grade"] <= grade_range[1])
    & (df["yr_built"] >= yr_range[0])
    & (df["yr_built"] <= yr_range[1])
)
if waterfront_opt == "Waterfront only":
    filt &= df["waterfront"] == 1
elif waterfront_opt == "Non-waterfront":
    filt &= df["waterfront"] == 0

filtered = df[filt]

st.caption(f"Showing **{len(filtered):,}** of {len(df):,} records after filters.")

if filtered.empty:
    st.info("No records match the current filters. Try relaxing the constraints.")
    st.stop()

# Price-encoded map
st.subheader("Price map")

sample_map = filtered.sample(min(4_000, len(filtered)), random_state=42)
p05 = float(sample_map["price"].quantile(0.05))
p95 = float(sample_map["price"].quantile(0.95))

fig_map = px.scatter_mapbox(
    sample_map,
    lat="lat",
    lon="long",
    color="price",
    color_continuous_scale="RdYlGn_r",
    range_color=[p05, p95],
    hover_data={"price": True, "bedrooms": True, "grade": True, "yr_built": True},
    zoom=9,
    height=480,
    mapbox_style="carto-positron",
    labels={"price": "Price (USD)"},
    opacity=0.65,
)
fig_map.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})
st.plotly_chart(fig_map, use_container_width=True)

# 2×2 chart grid
st.divider()

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Price distribution")
    fig_hist = px.histogram(
        filtered,
        x="price",
        nbins=60,
        color_discrete_sequence=["#2563eb"],
        labels={"price": "Price (USD)", "count": "Count"},
    )
    fig_hist.update_traces(marker_line_width=0.3, marker_line_color="white")
    fig_hist.update_layout(bargap=0.05)
    st.plotly_chart(fig_hist, use_container_width=True)

with row1_col2:
    st.subheader("Price by grade")
    df_box = filtered.copy()
    df_box["grade_str"] = df_box["grade"].astype(str)
    grade_order = [str(g) for g in sorted(df_box["grade"].unique())]
    fig_box = px.box(
        df_box,
        x="grade_str",
        y="price",
        color="grade_str",
        category_orders={"grade_str": grade_order},
        labels={"grade_str": "Grade", "price": "Price (USD)"},
        color_discrete_sequence=px.colors.sequential.Blues[3:],
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Price vs living area")
    scatter_sample = filtered.sample(min(2_000, len(filtered)), random_state=0)
    fig_scatter = px.scatter(
        scatter_sample,
        x="sqft_living",
        y="price",
        color="grade",
        color_continuous_scale="Blues",
        opacity=0.6,
        trendline="ols",
        labels={
            "sqft_living": "Living area (sqft)",
            "price": "Price (USD)",
            "grade": "Grade",
        },
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with row2_col2:
    st.subheader("Median price by year built")
    by_year = filtered.groupby("yr_built")["price"].median().reset_index()
    fig_line = px.line(
        by_year,
        x="yr_built",
        y="price",
        color_discrete_sequence=["#2563eb"],
        labels={"yr_built": "Year built", "price": "Median price (USD)"},
    )
    st.plotly_chart(fig_line, use_container_width=True)
