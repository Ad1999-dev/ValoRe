import uuid
from datetime import date

import plotly.express as px
import streamlit as st
from utils.api import health, predict
from utils.data import load_housing

st.set_page_config(page_title="Estimate Price · ValoRe", layout="wide")

st.title("Estimate Price")
st.caption(
    "Fill in the house details and get a live prediction from the deployed model."
)

# API-down submit guard
try:
    h = health()
    api_ok = bool(h.get("model_loaded"))
except Exception:
    h = None
    api_ok = False

if not api_ok:
    st.warning(
        "API is currently unreachable or has no model loaded. "
        "Predictions are disabled.",
        icon="⚠️",
    )
    st.stop()

# Market data for the result map and percentile bar
try:
    market_df = load_housing()
    market_loaded = True
except Exception:
    market_df = None
    market_loaded = False

# Location presets - saves the user from guessing King County coordinates
LOCATION_PRESETS = {
    "Custom (use sliders)": None,
    "Seattle (downtown)": (47.61, -122.33),
    "Bellevue": (47.61, -122.20),
    "Redmond": (47.67, -122.12),
    "Kirkland": (47.68, -122.21),
    "Issaquah": (47.53, -122.04),
    "Renton": (47.49, -122.21),
    "Federal Way": (47.32, -122.31),
}

# Top row - Sale date
st.divider()

sale_date = st.date_input(
    "Sale date",
    value=date.today(),
    min_value=date(2014, 1, 1),
    max_value=date(2030, 12, 31),
)
st.caption(
    "Defaults to today. Note: the model was trained on King County sales from "
    "May 2014 – May 2015, so dates far outside that window are extrapolations."
)

st.divider()

col1, col2, col3 = st.columns(3)

# Column 1 - Basics
with col1:
    st.markdown("**Basics**")
    bedrooms = st.slider("Bedrooms", 1, 10, 3)
    bathrooms = st.number_input(
        "Bathrooms", min_value=0.5, max_value=8.0, value=2.0, step=0.25
    )
    floors = st.select_slider(
        "Floors", options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5], value=1.0
    )

    sqft_living = st.slider("Living area (sqft)", 300, 13_000, 1_900, step=50)
    st.caption(f"≈ {sqft_living * 0.092903:,.0f} sqm")

    sqft_lot = st.slider("Lot size (sqft)", 500, 250_000, 7_600, step=500)
    st.caption(f"≈ {sqft_lot * 0.092903:,.0f} sqm")

    sqft_basement = st.slider("Basement (sqft)", 0, 5_000, 0, step=50)
    st.caption(
        f"≈ {sqft_basement * 0.092903:,.0f} sqm"
        + (" - no basement" if sqft_basement == 0 else "")
    )

# Column 2 - Quality
with col2:
    st.markdown("**Quality**")
    waterfront = st.toggle("Waterfront property")
    view = st.select_slider(
        "View",
        options=[0, 1, 2, 3, 4],
        value=0,
        format_func=lambda x: {
            0: "0 - None",
            1: "1 - Fair",
            2: "2 - Average",
            3: "3 - Good",
            4: "4 - Excellent",
        }[x],
    )
    condition = st.select_slider(
        "Condition",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: {
            1: "1 - Poor",
            2: "2 - Fair",
            3: "3 - Average",
            4: "4 - Good",
            5: "5 - Excellent",
        }[x],
    )
    grade = st.select_slider(
        "Grade",
        options=list(range(1, 14)),
        value=7,
        format_func=lambda x: {
            1: "1",
            2: "2",
            3: "3 - Poor",
            4: "4 - Low",
            5: "5 - Fair",
            6: "6 - Low average",
            7: "7 - Average",
            8: "8 - Good",
            9: "9 - Better",
            10: "10 - Very good",
            11: "11 - Excellent",
            12: "12 - Luxury",
            13: "13 - Mansion",
        }[x],
    )

# Column 3 - Year & location
with col3:
    st.markdown("**Year & location**")
    yr_built = st.slider("Year built", 1900, 2015, 1990)

    is_renovated = st.toggle("Has been renovated?")
    if is_renovated:
        yr_renovated = st.slider("Renovation year", 1934, 2015, 2000)
    else:
        yr_renovated = 0
        st.caption("Set to never renovated.")

    location_choice = st.selectbox(
        "Location preset",
        list(LOCATION_PRESETS.keys()),
        index=1,  # default = Seattle
    )

    preset_coords = LOCATION_PRESETS[location_choice]
    if preset_coords is None:
        lat = st.slider("Latitude", 47.15, 47.78, 47.50, step=0.01)
        lon = st.slider("Longitude", -122.52, -121.31, -122.10, step=0.01)
    else:
        lat, lon = preset_coords
        st.caption(f"📍 lat = {lat:.2f}, long = {lon:.2f}")

st.divider()

submitted = st.button("Estimate price", type="primary", use_container_width=True)

# Submit handler - POST /predict
if submitted:
    date_str = sale_date.strftime("%Y%m%d") + "T000000"

    payload = {
        # ── auto-handled by the dashboard (placeholders until API §1.7 cleanup) ──
        "id": uuid.uuid4().hex[:8],
        "zipcode": "98103",
        # ── computed / hidden defaults ──
        "date": date_str,
        "sqft_above": sqft_living - sqft_basement,
        "sqft_living15": sqft_living,
        "sqft_lot15": sqft_lot,
        # ── visible user inputs ──
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "sqft_living": sqft_living,
        "sqft_lot": sqft_lot,
        "sqft_basement": sqft_basement,
        "floors": floors,
        "waterfront": int(waterfront),
        "view": view,
        "condition": condition,
        "grade": grade,
        "yr_built": yr_built,
        "yr_renovated": yr_renovated,
        "lat": lat,
        "long": lon,
    }

    with st.spinner("Calling prediction API…"):
        try:
            result = predict(payload)
            st.session_state["last_prediction"] = {
                "price": result["prediction"],
                "payload": payload,
            }
        except Exception as e:
            st.error(f"Prediction failed: {e}")

# Result section
if "last_prediction" in st.session_state:
    lp = st.session_state["last_prediction"]
    price = lp["price"]
    p = lp["payload"]

    st.divider()
    st.subheader("Prediction result")

    res_col, map_col = st.columns([1, 2])

    with res_col:
        st.metric("Estimated price", f"${price:,.0f}")

        if market_loaded:
            percentile = (market_df["price"] < price).mean() * 100
            st.progress(min(int(percentile), 100) / 100)
            st.caption(
                f"Higher than **{percentile:.0f}%** of King County homes in the dataset."
            )

        st.markdown("**Input summary**")
        rev = f" · Renovated {p['yr_renovated']}" if p["yr_renovated"] else ""
        wf = "\n- 🌊 Waterfront property" if p["waterfront"] else ""
        date_pretty = f"{p['date'][:4]}-{p['date'][4:6]}-{p['date'][6:8]}"
        st.markdown(
            f"- {p['bedrooms']} bed · {p['bathrooms']} bath · "
            f"{p['floors']} floor(s)\n"
            f"- Living: {p['sqft_living']:,} sqft · Lot: {p['sqft_lot']:,} sqft\n"
            f"- Grade {p['grade']} · Condition {p['condition']} · View {p['view']}\n"
            f"- Built {p['yr_built']}{rev}\n"
            f"- Sale date: {date_pretty}{wf}"
        )

    with map_col:
        if market_loaded:
            sample = market_df.sample(min(3000, len(market_df)), random_state=42)
            fig = px.scatter_mapbox(
                sample,
                lat="lat",
                lon="long",
                color="price",
                color_continuous_scale="RdYlGn_r",
                range_color=[
                    sample["price"].quantile(0.05),
                    sample["price"].quantile(0.95),
                ],
                zoom=9,
                height=500,
                mapbox_style="carto-positron",
                labels={"price": "Price (USD)"},
                opacity=0.5,
            )
            fig.add_scattermapbox(
                lat=[p["lat"]],
                lon=[p["long"]],
                mode="markers",
                marker={"size": 18, "color": "blue"},
                name="Your house",
                hovertext=[f"Estimated: ${price:,.0f}"],
            )
            fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0}, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Market map unavailable (BigQuery not reachable).")
