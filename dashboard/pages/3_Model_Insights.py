from datetime import UTC, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.data import (
    MODEL_FEATURES,
    get_feature_importances,
    load_champion_model,
    score_sample,
)
from utils.registry import list_model_versions

st.set_page_config(page_title="Model Insights · ValoRe", layout="wide")

st.title("📊 Model Insights")
st.caption("The model behind every ValoRe prediction.")


def _lf(labels: dict, key: str):
    """Parse a float label (Vertex labels use `_` as decimal separator)."""
    val = labels.get(key, "")
    if not val:
        return None
    try:
        return float(val.replace("_", "."))
    except ValueError:
        return None


# Load registry
versions_raw = list_model_versions()
champion = None
has_registry = False

if not versions_raw:
    st.error(
        "Could not reach the Vertex AI Model Registry — only the static model card "
        "is shown below.",
        icon="⚠️",
    )
else:
    has_registry = True
    versions_raw = sorted(versions_raw, key=lambda v: v["create_time"])
    for i, v in enumerate(versions_raw, start=1):
        v["seq"] = i
    champion = next((v for v in versions_raw if v["is_default"]), None)


# Chapion model
if champion:
    st.subheader("Current champion")

    ct = champion["create_time"]
    if ct and ct.tzinfo is None:
        ct = ct.replace(tzinfo=UTC)
    days = (datetime.now(UTC) - ct).days if ct else None

    rmse = _lf(champion["labels"], "test_rmse")
    r2 = _lf(champion["labels"], "test_r2")

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Champion version",
        f"v{champion['seq']}",
        delta=(f"trained {days} day(s) ago" if days is not None else None),
        delta_color="off",
    )
    c2.metric("Test RMSE", f"${rmse:,.0f}" if rmse is not None else "—")
    c3.metric("Test R²", f"{r2:.4f}" if r2 is not None else "—")

    st.caption(
        f"Source: Vertex AI Model Registry · `valore-xgboost` · "
        f"version_id `{champion['version_id']}`"
    )
    st.divider()


# Version timeline
if has_registry:
    st.subheader("Version timeline")

    rows = []
    for v in versions_raw:
        ct = v["create_time"]
        if ct and ct.tzinfo is None:
            ct = ct.replace(tzinfo=UTC)
        rows.append(
            {
                "Version": f"v{v['seq']}",
                "Created": ct.strftime("%Y-%m-%d %H:%M UTC") if ct else "—",
                "Test RMSE ($)": _lf(v["labels"], "test_rmse"),
                "Test R²": _lf(v["labels"], "test_r2"),
                "Alias": "champion" if v["is_default"] else "—",
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Test RMSE ($)": st.column_config.NumberColumn(format="$%d"),
            "Test R²": st.column_config.NumberColumn(format="%.4f"),
        },
    )
    if champion:
        st.caption(
            f"{len(versions_raw)} version(s) registered · current default = "
            f"v{champion['seq']}."
        )
    else:
        st.caption(f"{len(versions_raw)} version(s) registered · no default alias set.")
    st.divider()


# Feature importance + Predicted vs Actual
if champion and champion.get("artifact_uri"):
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Feature Importance")
        try:
            with st.spinner("Loading champion model from GCS…"):
                model = load_champion_model(champion["artifact_uri"])

            imp_df = get_feature_importances(model, MODEL_FEATURES)
            if imp_df is None:
                st.info(
                    "Feature importances are not exposed by this model type.",
                    icon="ℹ️",
                )
            else:
                imp_df = imp_df.sort_values("importance", ascending=True)
                fig = px.bar(
                    imp_df,
                    x="importance",
                    y="feature",
                    orientation="h",
                    color="importance",
                    color_continuous_scale="Blues",
                )
                fig.update_layout(
                    height=520,
                    showlegend=False,
                    coloraxis_showscale=False,
                    xaxis_title="Importance (XGBoost gain)",
                    yaxis_title=None,
                    margin={"l": 0, "r": 0, "t": 10, "b": 0},
                )
                st.plotly_chart(fig, use_container_width=True)

                top3 = list(reversed(imp_df.tail(3)["feature"].tolist()))
                st.caption(
                    f"Top 3 drivers: **{', '.join(top3)}** · "
                    "feature importances from the trained XGBoost regressor "
                    "(higher = more decisive on price)."
                )
        except Exception as e:
            st.warning(f"Could not load feature importances: {e}", icon="⚠️")

    with col_r:
        st.subheader("Predicted vs Actual")
        try:
            with st.spinner("Scoring a 2,000-house sample from BigQuery…"):
                preds = score_sample(champion["artifact_uri"], n=2000)

            if preds.empty:
                st.info("Sample query returned no rows.", icon="ℹ️")
            else:
                ref_min = float(preds["actual"].min())
                ref_max = float(preds["actual"].max())

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=preds["actual"],
                        y=preds["predicted"],
                        mode="markers",
                        marker={
                            "size": 4,
                            "opacity": 0.55,
                            "color": preds["residual"].abs(),
                            "colorscale": "Reds",
                            "showscale": False,
                        },
                        name="Champion",
                        hovertemplate=(
                            "Actual: $%{x:,.0f}<br>Predicted: $%{y:,.0f}<extra></extra>"
                        ),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=[ref_min, ref_max],
                        y=[ref_min, ref_max],
                        mode="lines",
                        line={"color": "black", "dash": "dash", "width": 1},
                        name="Perfect fit (y = x)",
                    )
                )
                fig.update_layout(
                    xaxis_title="Actual price (USD)",
                    yaxis_title="Predicted price (USD)",
                    legend={"orientation": "h", "y": -0.2},
                    height=520,
                    margin={"l": 0, "r": 0, "t": 10, "b": 0},
                )
                st.plotly_chart(fig, use_container_width=True)

                st.caption(
                    f"{len(preds):,} houses sampled from BigQuery, scored with "
                    "the champion model. Dashed diagonal is `y = x` (perfect "
                    "prediction); deviations are residuals."
                )
        except Exception as e:
            st.warning(f"Could not generate fit plot: {e}", icon="⚠️")
