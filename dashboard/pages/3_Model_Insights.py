from datetime import UTC, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.data import load_test_predictions, load_training_slice
from utils.registry import list_model_versions

st.set_page_config(page_title="Model Insights · ValoRe", layout="wide")

st.title("📊 Model Insights")
st.caption("How ValoRe's model evolved as more training data arrived.")

# Load registry
versions_raw = list_model_versions()

if not versions_raw:
    st.info(
        "No model versions found in the Vertex AI registry. "
        "Run the continuous-training simulation (plan_sprint6.md) to populate this page.",
        icon="ℹ️",
    )
    st.stop()

# Sort oldest first, assign sequential display numbers
versions_raw = sorted(versions_raw, key=lambda v: v["create_time"])
for i, v in enumerate(versions_raw, start=1):
    v["seq"] = i


# Label parsing helpers
def _lf(labels: dict, key: str):
    """Parse a float label (uses _ as decimal separator per Vertex AI constraint)."""
    val = labels.get(key, "")
    if not val:
        return None
    try:
        return float(val.replace("_", "."))
    except ValueError:
        return None


def _li(labels: dict, key: str):
    """Parse an integer label."""
    val = labels.get(key, "")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


# Champion callout
champion = next((v for v in versions_raw if v["is_default"]), None)
if champion:
    ct = champion["create_time"]
    if ct:
        if ct.tzinfo is None:
            ct = ct.replace(tzinfo=UTC)
        days = (datetime.now(UTC) - ct).days
    else:
        days = "?"
    rmse = _lf(champion["labels"], "test_rmse")
    rmse_str = f" · RMSE ${rmse:,.0f}" if rmse else ""
    st.success(
        f"Current champion: v{champion['seq']}, registered {days} day(s) ago{rmse_str}.",
        icon="🏆",
    )

st.divider()

# Versions summary table
st.subheader("Registered versions")

rows = []
for v in versions_raw:
    labels = v["labels"]
    ct = v["create_time"]
    trained_at_lbl = labels.get("trained_at", "")
    if trained_at_lbl:
        trained_at_str = trained_at_lbl
    elif ct:
        if ct.tzinfo is None:
            ct = ct.replace(tzinfo=UTC)
        trained_at_str = ct.strftime("%Y-%m-%d %H:%M UTC")
    else:
        trained_at_str = "-"
    rows.append(
        {
            "Version": f"v{v['seq']}",
            "Trained at": trained_at_str,
            "Train size": _li(labels, "train_size"),
            "Test RMSE ($)": _lf(labels, "test_rmse"),
            "Test MAE ($)": _lf(labels, "test_mae"),
            "Test R²": _lf(labels, "test_r2"),
            "Champion": "✓" if v["is_default"] else "",
        }
    )

versions_df = pd.DataFrame(rows)
st.dataframe(
    versions_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Train size": st.column_config.NumberColumn(format="%d"),
        "Test RMSE ($)": st.column_config.NumberColumn(format="$%d"),
        "Test MAE ($)": st.column_config.NumberColumn(format="$%d"),
        "Test R²": st.column_config.NumberColumn(format="%.4f"),
    },
)
champ_label = next((f"v{v['seq']}" for v in versions_raw if v["is_default"]), "-")
st.caption(
    f"{len(versions_raw)} version(s) registered · current champion: {champ_label}."
)

# Metric trend bars
df_metrics = versions_df.dropna(subset=["Test RMSE ($)", "Test MAE ($)"])

if not df_metrics.empty:
    st.divider()
    st.subheader("Performance across versions")

    champ_rmse = _lf(champion["labels"], "test_rmse") if champion else None
    champ_mae = _lf(champion["labels"], "test_mae") if champion else None

    m_col1, m_col2 = st.columns(2)

    with m_col1:
        fig_rmse = px.bar(
            df_metrics,
            x="Version",
            y="Test RMSE ($)",
            color_discrete_sequence=["#dc2626"],
            labels={"Test RMSE ($)": "Test RMSE (USD)"},
            title="RMSE by version",
        )
        if champ_rmse:
            fig_rmse.add_hline(
                y=champ_rmse,
                line_dash="dash",
                line_color="gray",
                annotation_text="champion",
                annotation_position="bottom right",
            )
        st.plotly_chart(fig_rmse, use_container_width=True)

    with m_col2:
        fig_mae = px.bar(
            df_metrics,
            x="Version",
            y="Test MAE ($)",
            color_discrete_sequence=["#2563eb"],
            labels={"Test MAE ($)": "Test MAE (USD)"},
            title="MAE by version",
        )
        if champ_mae:
            fig_mae.add_hline(
                y=champ_mae,
                line_dash="dash",
                line_color="gray",
                annotation_text="champion",
                annotation_position="bottom right",
            )
        st.plotly_chart(fig_mae, use_container_width=True)

# Predicted vs actual + residual distributions
st.divider()
st.subheader("Test-set fit per version")

version_labels = [f"v{v['seq']}" for v in versions_raw]
selected_labels = st.multiselect(
    "Compare versions",
    options=version_labels,
    default=version_labels,
)
selected_seqs = {int(lbl[1:]) for lbl in selected_labels}

pred_data: dict[str, pd.DataFrame] = {}
for v in versions_raw:
    if v["seq"] not in selected_seqs or not v.get("artifact_uri"):
        continue
    df_pred = load_test_predictions(v["artifact_uri"])
    if not df_pred.empty:
        pred_data[f"v{v['seq']}"] = df_pred

if not pred_data:
    st.info(
        "No test predictions found. These are saved by the evaluation component "
        "in the Vertex AI pipeline - see plan_sprint6.md §S.4.4."
    )
else:
    fit_col, res_col = st.columns(2)

    all_actuals = pd.concat([d["actual"] for d in pred_data.values()])
    ref_min = float(all_actuals.min())
    ref_max = float(all_actuals.max())

    with fit_col:
        st.markdown("**Predicted vs. actual**")
        fig_pva = go.Figure()
        for name, df_p in pred_data.items():
            fig_pva.add_trace(
                go.Scatter(
                    x=df_p["actual"],
                    y=df_p["predicted"],
                    mode="markers",
                    name=name,
                    opacity=0.4,
                    marker={"size": 4},
                )
            )
        fig_pva.add_trace(
            go.Scatter(
                x=[ref_min, ref_max],
                y=[ref_min, ref_max],
                mode="lines",
                name="Perfect fit (y = x)",
                line={"color": "black", "dash": "dash", "width": 1},
            )
        )
        fig_pva.update_layout(
            xaxis_title="Actual price (USD)",
            yaxis_title="Predicted price (USD)",
            legend={"orientation": "h", "y": -0.2},
        )
        st.plotly_chart(fig_pva, use_container_width=True)

    with res_col:
        st.markdown("**Residual distributions**")
        fig_res = go.Figure()
        for name, df_p in pred_data.items():
            residuals = df_p["actual"] - df_p["predicted"]
            fig_res.add_trace(
                go.Histogram(
                    x=residuals,
                    name=name,
                    opacity=0.6,
                    histnorm="probability density",
                    nbinsx=50,
                )
            )
        fig_res.add_vline(
            x=0,
            line_dash="dash",
            line_color="black",
            annotation_text="zero error",
            annotation_position="top right",
        )
        fig_res.update_layout(
            barmode="overlay",
            xaxis_title="Residual (actual − predicted, USD)",
            yaxis_title="Density",
            legend={"orientation": "h", "y": -0.2},
        )
        st.plotly_chart(fig_res, use_container_width=True)

# Data drift: training-set distributions
if len(versions_raw) >= 2:
    v_first = versions_raw[0]
    v_last = versions_raw[-1]
    ts_first = _li(v_first["labels"], "train_size")
    ts_last = _li(v_last["labels"], "train_size")

    if ts_first and ts_last:
        st.divider()
        st.subheader("Training-data drift")

        drift_feature = st.selectbox(
            "Feature",
            ["price", "sqft_living", "grade", "yr_built", "lat", "long"],
        )

        try:
            with st.spinner("Loading training slices from BigQuery…"):
                df_v1 = load_training_slice(ts_first)
                df_vn = load_training_slice(ts_last)

            fig_drift = go.Figure()
            fig_drift.add_trace(
                go.Histogram(
                    x=df_v1[drift_feature],
                    name=f"v1 ({ts_first:,} rows)",
                    opacity=0.6,
                    marker_color="gray",
                    histnorm="probability density",
                    nbinsx=50,
                )
            )
            fig_drift.add_trace(
                go.Histogram(
                    x=df_vn[drift_feature],
                    name=f"v{v_last['seq']} ({ts_last:,} rows)",
                    opacity=0.6,
                    marker_color="#2563eb",
                    histnorm="probability density",
                    nbinsx=50,
                )
            )
            fig_drift.update_layout(
                barmode="overlay",
                xaxis_title=drift_feature,
                yaxis_title="Density",
            )
            st.plotly_chart(fig_drift, use_container_width=True)
            st.caption(
                f"Distribution of *{drift_feature}* in v1's training data "
                f"({ts_first:,} rows) vs v{v_last['seq']}'s training data "
                f"({ts_last:,} rows)."
            )
        except Exception as e:
            st.warning(f"Could not load training data for drift analysis: {e}")
