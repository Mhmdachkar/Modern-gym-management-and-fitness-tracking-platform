import os
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt


# ------------------------------
# Configuration
# ------------------------------
st.set_page_config(
    page_title="Gym Usage Dashboard",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)


DATA_DIR = os.path.join("phase4_data", "data")
OUTPUT_DIR = os.path.join("phase4_data", "outputs", "step 12 output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

USAGE_CSV = os.path.join(DATA_DIR, "gym_usage_data.csv")
COACH_CSV = os.path.join(DATA_DIR, "coach_performance_data.csv")
LAYOUT_CSV = os.path.join(DATA_DIR, "facility_layout_data.csv")
FACILITY_LOCATIONS_CSV = os.path.join(DATA_DIR, "facility_locations_data.csv")
PRESETS_JSON = os.path.join(OUTPUT_DIR, "dashboard_filter_presets.json")
AUDIT_LOG = os.path.join(OUTPUT_DIR, "output.txt")


# ------------------------------
# Data loading
# ------------------------------
@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def parse_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    if "check_in_time" in df.columns:
        df["check_in_time"] = pd.to_datetime(df["check_in_time"], errors="coerce")
    if "check_out_time" in df.columns:
        df["check_out_time"] = pd.to_datetime(df["check_out_time"], errors="coerce")
    return df


def derive_time_features(df: pd.DataFrame) -> pd.DataFrame:
    if "check_in_time" in df.columns and pd.api.types.is_datetime64_any_dtype(df["check_in_time"]):
        df["date"] = df["check_in_time"].dt.date
        df["hour"] = df["check_in_time"].dt.hour
        df["dayofweek"] = df["check_in_time"].dt.dayofweek
        df["weekday_name"] = df["check_in_time"].dt.day_name()
    # Peak hour flag
    if "peak_hour" in df.columns:
        df["peak_hour"] = df["peak_hour"].astype(str).str.lower().isin(["true", "1", "yes"]) | (df["peak_hour"] == True)
    return df


def utilization_by_zone(usage: pd.DataFrame, layout: pd.DataFrame) -> pd.DataFrame:
    if usage.empty:
        return pd.DataFrame(columns=["zone", "visits", "avg_duration", "capacity", "utilization_pct"])
    agg = (
        usage.groupby("zone").agg(visits=("usage_id", "count"), avg_duration=("duration_minutes", "mean")).reset_index()
    )
    cap = layout[["zone_name", "capacity"]].rename(columns={"zone_name": "zone"})
    out = agg.merge(cap, on="zone", how="left")
    out["capacity"] = out["capacity"].fillna(0)
    # Simple proxy for utilization: visits as proportion of capacity over period
    out["utilization_pct"] = np.where(out["capacity"] > 0, (out["visits"] / out["capacity"]) * 100.0, np.nan)
    return out


def log_event(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {message}\n")
    except Exception:
        pass


def load_presets() -> Dict[str, Any]:
    if not os.path.exists(PRESETS_JSON):
        return {}
    try:
        with open(PRESETS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_preset(name: str, state: Dict[str, Any]) -> None:
    presets = load_presets()
    presets[name] = state
    with open(PRESETS_JSON, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2)
    log_event(f"Saved preset '{name}'")


# ------------------------------
# UI - Sidebar Filters
# ------------------------------
st.sidebar.title("Controls")

# Role-based view
role = st.sidebar.selectbox("Role", ["Manager", "Coach"], index=0)
coach_scope = None
if role == "Coach":
    # Let a coach pick their ID if multiple
    try:
        usage_tmp = pd.read_csv(USAGE_CSV)
        coach_ids = sorted(usage_tmp.get("coach_id", pd.Series(dtype=float)).dropna().unique().tolist())
    except Exception:
        coach_ids = []
    coach_scope = st.sidebar.selectbox("Your Coach ID", coach_ids) if coach_ids else None

st.sidebar.subheader("Filters")

usage_df = load_csv(USAGE_CSV)
coach_df = load_csv(COACH_CSV)
layout_df = load_csv(LAYOUT_CSV)
facility_loc_df = load_csv(FACILITY_LOCATIONS_CSV) if os.path.exists(FACILITY_LOCATIONS_CSV) else pd.DataFrame()

usage_df = parse_datetime_columns(usage_df)
usage_df = derive_time_features(usage_df)

# Date range
if not usage_df.empty and "check_in_time" in usage_df.columns:
    min_date = usage_df["check_in_time"].min().date()
    max_date = usage_df["check_in_time"].max().date()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
else:
    date_range = None

# Facility filter
facility_options = sorted(usage_df["facility_id"].dropna().unique().tolist()) if "facility_id" in usage_df.columns else []
facility_selected = st.sidebar.multiselect("Facility", facility_options, default=facility_options)

# Zone filter
zone_options = sorted(usage_df["zone"].dropna().unique().tolist()) if "zone" in usage_df.columns else []
zone_selected = st.sidebar.multiselect("Zone", zone_options, default=zone_options[:10])

# Activity type filter
activity_options = sorted(usage_df["activity_type"].dropna().unique().tolist()) if "activity_type" in usage_df.columns else []
activity_selected = st.sidebar.multiselect("Activity Type", activity_options, default=activity_options)

# Coach filter
coach_options = sorted(usage_df["coach_id"].dropna().unique().tolist()) if "coach_id" in usage_df.columns else []
coach_selected = st.sidebar.multiselect("Coach ID", coach_options)

# Peak hour toggle
peak_only = st.sidebar.checkbox("Show peak hours only", value=False)

# Apply filters
filtered = usage_df.copy()
if date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["check_in_time"] >= start) & (filtered["check_in_time"] <= (end + pd.Timedelta(days=1)))]
if facility_selected:
    filtered = filtered[filtered["facility_id"].isin(facility_selected)]
if zone_selected:
    filtered = filtered[filtered["zone"].isin(zone_selected)]
if activity_selected:
    filtered = filtered[filtered["activity_type"].isin(activity_selected)]
if coach_selected:
    filtered = filtered[filtered["coach_id"].isin(coach_selected)]
# Enforce coach scoping
if coach_scope is not None:
    filtered = filtered[filtered["coach_id"] == coach_scope]
if peak_only and "peak_hour" in filtered.columns:
    filtered = filtered[filtered["peak_hour"] == True]

# Presets (save/load)
st.sidebar.subheader("Presets")
presets = load_presets()
preset_names = ["<None>"] + sorted(presets.keys())
selected_preset = st.sidebar.selectbox("Load preset", preset_names, index=0)
if selected_preset != "<None>":
    p = presets.get(selected_preset, {})
    # We won’t re-render sidebar controls mid-run; instead apply to filtered DF by re-running with state in the future.
    st.sidebar.info(f"Preset loaded: {selected_preset}. Re-select filters if needed to mirror preset.")

new_preset_name = st.sidebar.text_input("Save current filters as…", value="")
if st.sidebar.button("Save preset") and new_preset_name.strip():
    preset_state = {
        "date_range": [str(date_range[0]), str(date_range[1])] if date_range else None,
        "facility_selected": facility_selected,
        "zone_selected": zone_selected,
        "activity_selected": activity_selected,
        "coach_selected": coach_selected,
        "peak_only": bool(peak_only),
        "role": role,
        "coach_scope": coach_scope,
    }
    save_preset(new_preset_name.strip(), preset_state)
    st.sidebar.success(f"Preset '{new_preset_name.strip()}' saved")


# ------------------------------
# Header and KPIs
# ------------------------------
st.title("🏋️ Gym Usage Dashboard")
st.caption("Interactive monitoring of usage, coach performance, and facility utilization")

col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
total_visits = int(filtered["usage_id"].nunique()) if "usage_id" in filtered.columns else len(filtered)
unique_members = int(filtered["member_id"].nunique()) if "member_id" in filtered.columns else 0
avg_duration = float(filtered["duration_minutes"].mean()) if "duration_minutes" in filtered.columns and not filtered.empty else 0.0
peak_hour = int(filtered["hour"].mode().iloc[0]) if "hour" in filtered.columns and not filtered.empty else np.nan
avg_rating = float(filtered["member_rating"].mean()) if "member_rating" in filtered.columns and not filtered.empty else np.nan

col_kpi1.metric("Total Visits", f"{total_visits}")
col_kpi2.metric("Unique Members", f"{unique_members}")
col_kpi3.metric("Avg Duration (min)", f"{avg_duration:.1f}")
col_kpi4.metric("Peak Hour", f"{peak_hour if not np.isnan(peak_hour) else '-'}")
col_kpi5.metric("Avg Member Rating", f"{avg_rating:.2f}" if not np.isnan(avg_rating) else "-")


# ------------------------------
# Tabs
# ------------------------------
tab_overview, tab_heatmaps, tab_coach, tab_facility = st.tabs([
    "Overview",
    "Heatmaps",
    "Coach Performance",
    "Facility Utilization",
])


# ------------------------------
# Overview Tab
# ------------------------------
with tab_overview:
    st.subheader("Overview")
    c1, c2 = st.columns(2)

    # Visits by day of week
    if not filtered.empty and "weekday_name" in filtered.columns:
        dow_counts = (
            filtered.groupby("weekday_name")["usage_id"].count().reindex(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], fill_value=0
            )
        )
        fig_dow = px.bar(dow_counts, labels={"value": "Visits", "weekday_name": "Day of Week"}, title="Visits by Day of Week")
        c1.plotly_chart(fig_dow, use_container_width=True)
        if st.button("Export 'Visits by Day of Week' chart (HTML)"):
            path = os.path.join(OUTPUT_DIR, "visits_by_dow.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fig_dow.to_html(full_html=True, include_plotlyjs="cdn"))
            log_event("Exported visits_by_dow.html")
            st.success(f"Saved {path}")

    # Activity type share
    if not filtered.empty and "activity_type" in filtered.columns:
        act_counts = filtered["activity_type"].value_counts()
        fig_act = px.pie(
            names=act_counts.index,
            values=act_counts.values,
            title="Activity Type Share",
            hole=0.35,
        )
        c2.plotly_chart(fig_act, use_container_width=True)
        if st.button("Export 'Activity Type Share' chart (HTML)"):
            path = os.path.join(OUTPUT_DIR, "activity_type_share.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fig_act.to_html(full_html=True, include_plotlyjs="cdn"))
            log_event("Exported activity_type_share.html")
            st.success(f"Saved {path}")

    # Visits over time
    if not filtered.empty and "date" in filtered.columns:
        ts = filtered.groupby("date").size().reset_index(name="visits")
        fig_ts = px.line(ts, x="date", y="visits", markers=True, title="Visits Over Time")
        st.plotly_chart(fig_ts, use_container_width=True)
        if st.button("Export 'Visits Over Time' chart (HTML)"):
            path = os.path.join(OUTPUT_DIR, "visits_over_time.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fig_ts.to_html(full_html=True, include_plotlyjs="cdn"))
            log_event("Exported visits_over_time.html")
            st.success(f"Saved {path}")


# ------------------------------
# Heatmaps Tab
# ------------------------------
with tab_heatmaps:
    st.subheader("Usage Heatmaps")
    hc1, hc2 = st.columns(2)

    # Hour x Day heatmap
    if not filtered.empty and {"hour", "weekday_name"}.issubset(filtered.columns):
        pivot1 = (
            filtered.pivot_table(index="weekday_name", columns="hour", values="usage_id", aggfunc="count", fill_value=0)
            .reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], axis=0)
        )
        fig_hm1 = px.imshow(
            pivot1,
            labels=dict(x="Hour of Day", y="Day of Week", color="Visits"),
            title="Visits Heatmap (Day x Hour)",
            aspect="auto",
            color_continuous_scale="Viridis",
        )
        hc1.plotly_chart(fig_hm1, use_container_width=True)
        if st.button("Export Day x Hour Heatmap (HTML)"):
            path = os.path.join(OUTPUT_DIR, "heatmap_day_hour.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fig_hm1.to_html(full_html=True, include_plotlyjs="cdn"))
            log_event("Exported heatmap_day_hour.html")
            st.success(f"Saved {path}")

    # Zone x Hour heatmap
    if not filtered.empty and {"zone", "hour"}.issubset(filtered.columns):
        pivot2 = filtered.pivot_table(index="zone", columns="hour", values="usage_id", aggfunc="count", fill_value=0)
        # Keep top 20 zones by visits to avoid oversize visuals
        top_zones = filtered["zone"].value_counts().head(20).index
        pivot2 = pivot2.loc[pd.Index(top_zones).intersection(pivot2.index)]
        fig_hm2 = px.imshow(
            pivot2,
            labels=dict(x="Hour of Day", y="Zone", color="Visits"),
            title="Visits Heatmap (Zone x Hour)",
            aspect="auto",
            color_continuous_scale="Plasma",
        )
        hc2.plotly_chart(fig_hm2, use_container_width=True)
        if st.button("Export Zone x Hour Heatmap (HTML)"):
            path = os.path.join(OUTPUT_DIR, "heatmap_zone_hour.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fig_hm2.to_html(full_html=True, include_plotlyjs="cdn"))
            log_event("Exported heatmap_zone_hour.html")
            st.success(f"Saved {path}")


# ------------------------------
# Coach Performance Tab
# ------------------------------
with tab_coach:
    st.subheader("Coach Performance")

    if coach_df.empty:
        st.info("Coach performance data is not available.")
    else:
        # KPI cards
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("Coaches", f"{coach_df['coach_id'].nunique()}")
        cc2.metric("Total Bookings", f"{int(coach_df['total_bookings'].sum())}")
        cc3.metric("Avg Rating", f"{coach_df['avg_rating'].mean():.2f}")
        cc4.metric("Avg Satisfaction", f"{coach_df['member_satisfaction'].mean():.2f}")

        # Table
        st.dataframe(coach_df.sort_values(["total_bookings", "avg_rating"], ascending=[False, False]), use_container_width=True)

        # Charts
        ch1, ch2 = st.columns(2)
        fig_cb = px.bar(
            coach_df.sort_values("total_bookings", ascending=False).head(15),
            x="coach_name",
            y="total_bookings",
            color="avg_rating",
            title="Top Coaches by Bookings",
            color_continuous_scale="Blues",
        )
        ch1.plotly_chart(fig_cb, use_container_width=True)

        fig_ns = px.scatter(
            coach_df,
            x="no_shows",
            y="avg_rating",
            size="total_bookings",
            color="member_satisfaction",
            hover_name="coach_name",
            title="No-Shows vs Rating (bubble size = bookings)",
            color_continuous_scale="RdYlGn",
        )
        ch2.plotly_chart(fig_ns, use_container_width=True)

        # Export button (Manager-only)
        if role == "Manager" and st.button("Export Coach Performance (CSV)"):
            export_path = os.path.join(OUTPUT_DIR, "dashboard_coach_performance.csv")
            coach_df.to_csv(export_path, index=False)
            log_event("Exported dashboard_coach_performance.csv")
            st.success(f"Exported to {export_path}")


# ------------------------------
# Facility Utilization Tab
# ------------------------------
with tab_facility:
    st.subheader("Facility Utilization")

    if filtered.empty:
        st.info("No usage data for current filters.")
    else:
        util_df = utilization_by_zone(filtered, layout_df)
        fc1, fc2 = st.columns(2)

        # Utilization by zone
        fig_util = px.bar(
            util_df.sort_values("utilization_pct", ascending=False),
            x="zone",
            y="utilization_pct",
            title="Zone Utilization (%)",
        )
        fc1.plotly_chart(fig_util, use_container_width=True)

        # Duration by zone
        fig_dur = px.bar(
            util_df.sort_values("avg_duration", ascending=False),
            x="zone",
            y="avg_duration",
            title="Average Duration by Zone (min)",
        )
        fc2.plotly_chart(fig_dur, use_container_width=True)

        # Facility summary export (live from filtered data) - Manager-only
        if role == "Manager" and st.button("Export Facility Summary (CSV)"):
            summary = pd.DataFrame({
                "facility_id": [int(filtered["facility_id"].iloc[0])] if "facility_id" in filtered.columns and not filtered.empty else [np.nan],
                "usage_id_count": [int(filtered.shape[0])],
                "duration_minutes_mean": [float(filtered["duration_minutes"].mean()) if "duration_minutes" in filtered.columns else np.nan],
                "duration_minutes_sum": [float(filtered["duration_minutes"].sum()) if "duration_minutes" in filtered.columns else np.nan],
                "member_rating_mean": [float(filtered["member_rating"].mean()) if "member_rating" in filtered.columns else np.nan],
                "no_show_sum": [int(filtered["no_show"].sum()) if "no_show" in filtered.columns else 0],
            })
            export_path = os.path.join(OUTPUT_DIR, "dashboard_facility_summary.csv")
            summary.to_csv(export_path, index=False)
            log_event("Exported dashboard_facility_summary.csv")
            st.success(f"Exported to {export_path}")

        # Download filtered usage as CSV (role-agnostic)
        if not filtered.empty:
            dl_csv = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download filtered usage CSV",
                data=dl_csv,
                file_name="filtered_usage.csv",
                mime="text/csv",
            )


# ------------------------------
# Footer
# ------------------------------
st.caption("Data sources: gym_usage_data.csv, coach_performance_data.csv, facility_layout_data.csv")


