import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="RR 2027 | Pressure Index Analytics",
    page_icon="🏏",
    layout="wide"
)

# ==========================================
# DESIGN
# ==========================================
st.markdown("""
<style>
.stApp { background: #080D1B; color: white; }
[data-testid="stSidebar"] { background: #10182B; }
h1, h2, h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA LOCATION
# ==========================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" if (BASE_DIR / "data").exists() else BASE_DIR

@st.cache_data
def load_csv(filename):
    path = DATA_DIR / filename
    if not path.exists():
        alt_path = BASE_DIR / filename
        if alt_path.exists():
            path = alt_path
        else:
            zipped = path.with_suffix(".zip")
            if zipped.exists():
                path = zipped
            else:
                st.error(f"Missing data file: {filename}")
                return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)

rankings = load_csv("Player_Rankings.csv")
batters = load_csv("Batters_By_Format.csv")
bowlers = load_csv("Bowlers_By_Format.csv")
deliveries = load_csv("Pressure_Deliveries.csv")
summary = load_csv("Pressure_Summary.csv")

if rankings.empty or batters.empty or bowlers.empty:
    st.warning("Required data files are missing. Please upload all 5 CSV files.")
    st.stop()

# ==========================================
# HEADER
# ==========================================
st.markdown("# 🏏 PRESSURE INDEX ANALYTICS")
st.markdown("### Rajasthan Royals | IPL 2027 Auction Intelligence")
st.caption("Identifying reliable players through ball-by-ball pressure performance analysis.")
st.divider()

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.markdown("# 🏏 RR ANALYTICS")
st.sidebar.caption("IPL 2027 Auction Intelligence")

page = st.sidebar.radio(
    "NAVIGATION",
    ["Executive Overview", "Batter Analytics", "Bowler Analytics",
     "Format Comparison", "Player Explorer", "Dataset Information"]
)
st.sidebar.divider()
st.sidebar.success(f"{len(deliveries):,} pressure deliveries loaded")

def top_bar(df, x, y, colors, title=None, height=450):
    fig = px.bar(
        df.sort_values(x), x=x, y=y, orientation="h", text_auto=".2f",
        color=x, color_continuous_scale=colors, title=title
    )
    fig.update_layout(template="plotly_dark", height=height,
                      showlegend=False, coloraxis_showscale=False)
    return fig

# ==========================================
# EXECUTIVE OVERVIEW
# ==========================================
if page == "Executive Overview":
    st.subheader("📊 Executive Overview")

    total_players = rankings["Player"].nunique() if "Player" in rankings else 0
    total_batters = batters["striker_name"].nunique() if "striker_name" in batters else 0
    total_bowlers = bowlers["bowler_name"].nunique() if "bowler_name" in bowlers else 0
    total_deliveries = len(deliveries)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PLAYERS ANALYSED", f"{total_players:,}")
    c2.metric("UNIQUE BATTERS", f"{total_batters:,}")
    c3.metric("UNIQUE BOWLERS", f"{total_bowlers:,}")
    c4.metric("PRESSURE DELIVERIES", f"{total_deliveries:,}")

    st.divider()
    left, right = st.columns(2)

    with left:
        st.markdown("### ⭐ TOP 10 BATTERS")
        top = rankings[rankings["Role"].astype(str).str.lower() == "batter"].nlargest(10, "Score")
        st.plotly_chart(top_bar(top, "Score", "Player", ["#293B5B", "#FF4F9A"]), use_container_width=True)

    with right:
        st.markdown("### 🎯 TOP 10 BOWLERS")
        top = rankings[rankings["Role"].astype(str).str.lower() == "bowler"].nlargest(10, "Score")
        st.plotly_chart(top_bar(top, "Score", "Player", ["#293B5B", "#00C2FF"]), use_container_width=True)

    st.divider()
    st.markdown("### 📌 PROJECT OBJECTIVE")
    st.info(
        "Identify players who demonstrate reliability and performance "
        "under high-pressure situations, supporting Rajasthan Royals "
        "in making informed IPL 2027 auction decisions."
    )

# ==========================================
# BATTER ANALYTICS
# ==========================================
elif page == "Batter Analytics":
    st.subheader("🏏 BATTER PERFORMANCE ANALYTICS")

    formats = ["All"] + sorted(batters["league"].dropna().unique().tolist())
    selected = st.selectbox("Select Competition", formats)

    filtered = batters.copy()
    if selected != "All":
        filtered = filtered[filtered["league"] == selected]

    top = filtered.nlargest(15, "batting_score")
    st.plotly_chart(top_bar(top, "batting_score", "striker_name", ["#293B5B", "#FF4F9A"],
                            "TOP 15 BATTERS UNDER PRESSURE", 650), use_container_width=True)

    st.markdown("### 📋 COMPLETE BATTER RANKINGS")
    st.dataframe(filtered.sort_values("batting_score", ascending=False),
                 use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download Batter Rankings", filtered.to_csv(index=False),
                       "Batter_Rankings.csv", "text/csv")

# ==========================================
# BOWLER ANALYTICS
# ==========================================
elif page == "Bowler Analytics":
    st.subheader("🎯 BOWLER PERFORMANCE ANALYTICS")

    formats = ["All"] + sorted(bowlers["league"].dropna().unique().tolist())
    selected = st.selectbox("Select Competition", formats)

    filtered = bowlers.copy()
    if selected != "All":
        filtered = filtered[filtered["league"] == selected]

    top = filtered.nlargest(15, "bowling_score")
    st.plotly_chart(top_bar(top, "bowling_score", "bowler_name", ["#293B5B", "#00C2FF"],
                            "TOP 15 BOWLERS UNDER PRESSURE", 650), use_container_width=True)

    st.markdown("### 📋 COMPLETE BOWLER RANKINGS")
    st.dataframe(filtered.sort_values("bowling_score", ascending=False),
                 use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download Bowler Rankings", filtered.to_csv(index=False),
                       "Bowler_Rankings.csv", "text/csv")

# ==========================================
# FORMAT COMPARISON
# ==========================================
elif page == "Format Comparison":
    st.subheader("🌍 IPL vs T20I COMPARISON")

    batter_format = batters.groupby("league")["batting_score"].mean().reset_index()
    bowler_format = bowlers.groupby("league")["bowling_score"].mean().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Batter Score Comparison")
        fig = px.bar(batter_format, x="league", y="batting_score", color="league",
                     text_auto=".2f", title="Average Batter Pressure Score")
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("### Bowler Score Comparison")
        fig = px.bar(bowler_format, x="league", y="bowling_score", color="league",
                     text_auto=".2f", title="Average Bowler Pressure Score")
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("### Format-wise Batter Data")
    st.dataframe(batter_format, use_container_width=True, hide_index=True)
    st.markdown("### Format-wise Bowler Data")
    st.dataframe(bowler_format, use_container_width=True, hide_index=True)

# ==========================================
# PLAYER EXPLORER
# ==========================================
elif page == "Player Explorer":
    st.subheader("🔎 PLAYER EXPLORER")

    players = sorted(rankings["Player"].dropna().unique().tolist())
    selected_player = st.selectbox("Search Player", players)
    result = rankings[rankings["Player"] == selected_player]

    if not result.empty:
        row = result.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("PLAYER", row["Player"])
        c2.metric("PRESSURE SCORE", round(row["Score"], 2))
        c3.metric("OVERALL RANK", int(row["Rank"]))

        st.divider()
        st.markdown("### PLAYER PERFORMANCE DETAILS")
        st.dataframe(result, use_container_width=True, hide_index=True)

        bat = batters[batters["striker_name"] == selected_player]
        bowl = bowlers[bowlers["bowler_name"] == selected_player]
        if not bat.empty:
            st.markdown("### FORMAT-WISE BATTING PERFORMANCE")
            st.dataframe(bat, use_container_width=True, hide_index=True)
        if not bowl.empty:
            st.markdown("### FORMAT-WISE BOWLING PERFORMANCE")
            st.dataframe(bowl, use_container_width=True, hide_index=True)

# ==========================================
# DATASET INFORMATION
# ==========================================
elif page == "Dataset Information":
    st.subheader("📚 DATASET INFORMATION & METHODOLOGY")
    st.markdown("### DATASET OVERVIEW")

    files = {
        "Player Rankings": rankings, "Batter Analysis": batters,
        "Bowler Analysis": bowlers, "Pressure Deliveries": deliveries,
        "Pressure Summary": summary
    }
    for name, df in files.items():
        with st.expander(name):
            c1, c2 = st.columns(2)
            c1.metric("Rows", f"{len(df):,}")
            c2.metric("Columns", len(df.columns))
            st.dataframe(df.head(10), use_container_width=True)

    st.divider()
    st.markdown("### ANALYTICAL FRAMEWORK")
    st.write("""
    **1. Data Cleaning:** Ball-by-ball IPL & T20I data excluding DLS-affected matches, super overs, and incomplete games.

    **2. High-Pressure Delivery Identification:** Deliveries meeting at least 2 of 3 format-specific quartile pressure triggers:
    - *2nd Innings (Chases):* Required Run Rate > 75th percentile, Wickets Lost >= 75th percentile, or Balls Remaining <= 25th percentile.
    - *1st Innings (Setting Target):* Par Score Deficit <= 25th percentile, Wickets Lost >= 75th percentile, or Balls Remaining <= 25th percentile.

    **3. Sample Size & Empirical Bayes Shrinkage:** Minimum threshold of 80 high-pressure balls and 120 normal balls, smoothed toward the format average (`PRIOR_BALLS = 100`) to prevent small-sample inflation.

    **4. Batter Evaluation:** Weighted percentile index combining Pressure Strike Rate (30%), Strike Rate Delta vs. Normal Baseline (20%), Dismissal Rate (20%), Boundary % (15%), and Dot Ball % (15%).

    **5. Bowler Evaluation:** Weighted percentile index combining Pressure Economy (30%), Economy Delta vs. Normal Baseline (20%), Bowling Average with zero-wicket penalty floor (20%), Bowling Strike Rate (15%), and Dot Ball % (15%).

    **6. Cross-Format Aggregation:** Ball-weighted aggregation across IPL (1.15x parity multiplier) and T20I (1.00x) with a volume confidence factor.
    """)

# ==========================================
# FOOTER
# ==========================================
st.divider()
st.markdown("""
<center>
<p style="color:#8999B5">
PRESSURE INDEX ANALYTICS | RAJASTHAN ROYALS 2027<br>
Cricket Intelligence • Performance Analytics • Data-Driven Decisions
</p>
</center>
""", unsafe_allow_html=True)
