
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import requests

SIG_CONFIGS = {
    "SIG 1": {"station_id": 40611, "default_index": "ERC"},
    "SIG 2": {"station_id": 41001, "default_index": "BI"},
    "SIG 3": {"station_id": 42201, "default_index": "SC"}
}
INDEX_OPTIONS = ["ERC", "BI", "IC", "SC", "KBDI", "100Hr", "1000Hr", "Woody FM", "Herb FM"]
COLOR_MAP = {1: "green", 2: "yellow", 3: "orange", 4: "red", 5: "purple", 6: "black"}

def classify(value, breakpoints):
    for i, bp in enumerate(breakpoints):
        if value <= bp:
            return i + 1
    return len(breakpoints) + 1

st.title("🔥 Multi-SIG NFDRS Dashboard")

# --- SIG & Index Selection ---
selected_sigs = st.multiselect("Select SIGs", list(SIG_CONFIGS.keys()), default=["SIG 1"])
selected_indices = st.multiselect("Select Indices", INDEX_OPTIONS, default=["ERC"])

# --- Percentile Band Selection ---
band_type = st.selectbox("Select Percentile Band Overlay", ["80/95", "90/97", "Custom"])
if band_type == "Custom":
    custom_low = st.number_input("Custom Band Lower", value=70)
    custom_high = st.number_input("Custom Band Upper", value=90)
else:
    custom_low, custom_high = (80, 95) if band_type == "80/95" else (90, 97)

# --- Breakpoints Input ---
breakpoints = st.text_input("Breakpoints (comma-separated)", "20,40,60,80")
try:
    bp = list(map(int, breakpoints.split(",")))
except:
    bp = [20, 40, 60, 80]
    st.warning("Invalid breakpoints. Default used.")

# --- Tabs Layout ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📅 Daily Listings", "⚙️ Configuration", "📈 Climatology"])

# --- Tab 1: Dashboard with Multi-SIG, Percentile Bands ---
with tab1:
    for sig in selected_sigs:
        st.subheader(f"{sig} Outputs")
        station_id = SIG_CONFIGS[sig]["station_id"]

        try:
            url = f"https://fems.fs2c.usda.gov/api/climatology/download-nfdr-daily-summary/?dataset=all&startDate=2025-05-01&endDate=2025-05-25&dataFormate=csv&stationIds={station_id}&fuelModels=Y"
            df = pd.read_csv(BytesIO(requests.get(url).content))
            df["sample_date"] = pd.to_datetime(df["sample_date"])

            for idx in selected_indices:
                if idx.lower() not in df.columns.str.lower():
                    continue
                col = [c for c in df.columns if c.lower() == idx.lower()][0]
                df["class"] = [classify(v, bp) for v in df[col]]

                fig, ax = plt.subplots()
                ax.bar(df["sample_date"], df[col], color=[COLOR_MAP.get(c, 'gray') for c in df["class"]])
                ax.axhspan(custom_low, custom_high, color="orange", alpha=0.2, label=f"{custom_low}-{custom_high} percentile")
                ax.set_title(f"{sig} - {idx}")
                ax.set_xlabel("Date")
                ax.set_ylabel(idx)
                ax.legend()
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Error loading data for {sig}: {e}")

# --- Tab 2: Daily Listings ---
with tab2:
    st.header("Daily Listings")
    for sig in selected_sigs:
        station_id = SIG_CONFIGS[sig]["station_id"]
        try:
            url = f"https://fems.fs2c.usda.gov/api/climatology/download-nfdr-daily-summary/?dataset=all&startDate=2025-05-01&endDate=2025-05-25&dataFormate=csv&stationIds={station_id}&fuelModels=Y"
            df = pd.read_csv(BytesIO(requests.get(url).content))
            df["sample_date"] = pd.to_datetime(df["sample_date"])
            st.subheader(f"{sig}")
            st.dataframe(df[["sample_date"] + selected_indices])
            csv = df[["sample_date"] + selected_indices].to_csv(index=False).encode("utf-8")
            st.download_button(f"Download CSV for {sig}", data=csv, file_name=f"{sig}_daily_listing.csv", mime="text/csv")
        except:
            st.error(f"Could not load daily listing for {sig}")

# --- Tab 3: Configuration ---
with tab3:
    st.header("Current Config")
    config_df = pd.DataFrame([{
        "SIGs": "; ".join(selected_sigs),
        "Indices": "; ".join(selected_indices),
        "Breakpoints": breakpoints,
        "Percentile Band": f"{custom_low}-{custom_high}"
    }])
    st.dataframe(config_df)
    st.download_button("Download Configuration", data=config_df.to_csv(index=False), file_name="dashboard_config.csv", mime="text/csv")

# --- Tab 4: Climatology Overlay ---
with tab4:
    st.header("Climatology Comparison (2005–2022)")
    for sig in selected_sigs:
        station_id = SIG_CONFIGS[sig]["station_id"]
        hist_url = f"https://fems.fs2c.usda.gov/api/climatology/download-nfdr-daily-summary/?dataset=climatology&startDate=2005-01-01&endDate=2022-12-31&dataFormate=csv&stationIds={station_id}&fuelModels=Y"
        cur_url = f"https://fems.fs2c.usda.gov/api/climatology/download-nfdr-daily-summary/?dataset=all&startDate=2025-05-01&endDate=2025-05-25&dataFormate=csv&stationIds={station_id}&fuelModels=Y"
        try:
            df_hist = pd.read_csv(BytesIO(requests.get(hist_url).content))
            df_hist["sample_date"] = pd.to_datetime(df_hist["sample_date"])
            df_obs = pd.read_csv(BytesIO(requests.get(cur_url).content))
            df_obs["sample_date"] = pd.to_datetime(df_obs["sample_date"])
            for idx in selected_indices:
                if idx.lower() not in df_hist.columns.str.lower():
                    continue
                col = [c for c in df_hist.columns if c.lower() == idx.lower()][0]
                fig, ax = plt.subplots()
                ax.plot(df_hist["sample_date"], df_hist[col], alpha=0.3, label="Historical")
                ax.plot(df_obs["sample_date"], df_obs[col], label="Observed", color="blue")
                ax.set_title(f"{sig} - {idx} Climatology")
                ax.set_xlabel("Date")
                ax.set_ylabel(idx)
                ax.legend()
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Error loading climatology for {sig}: {e}")
