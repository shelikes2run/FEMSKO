import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import requests

# Dropdown options from spreadsheet
fuel_models = ["V - Grass", "W - Grass/Shrub", "X - Brush", "Y - Timber", "Z - Slash"]
index_options = ["ERC", "BI", "1000hr", "SC"]
breakpoint_options = ["90/97 percentile", "80/95 percentile", "Custom"]
class_options = ["3", "4", "5", "6"]

fems_url = "https://fems.fs2c.usda.gov/fuelmodel/sample/download?returnAll=&responseFormat=csv&siteId=All&sampleId=&startDate=2025-02-23T00:00:00.000Z&endDate=2025-03-25T23:00:00.000Z&filterByFuelId=&filterByStatus=Submitted&filterByCategory=All&filterBySubCategory=All&filterByMethod=All&sortBy=fuel_type&sortOrder=asc"

st.title("FEMS Dispatch Staffing Dashboard")

with st.form("sig_form"):
    st.subheader("SIG Configuration")

    sig_selection = st.selectbox("Select SIG:", ["PSA NC02", "Oak Knoll RAWS", "Redding RAWS"])
    fuel_model = st.selectbox("Fuel Model:", fuel_models)
    number_of_raws = st.number_input("Number of RAWS:", min_value=1, max_value=50, value=10)

    st.markdown("---")
    st.subheader("Staffing Level Inputs")

    staffing_index = st.selectbox("Staffing Index Type:", index_options)
    staffing_breakpoint = st.selectbox("Staffing Breakpoint:", breakpoint_options)
    custom_staffing_breakpoint = None
    if staffing_breakpoint == "Custom":
        custom_staffing_breakpoint = st.text_input("Enter Custom Breakpoints (comma-separated):")

    st.markdown("---")
    st.subheader("Dispatch Level Inputs")

    dispatch_index = st.selectbox("Dispatch Index Type:", index_options)
    number_of_classes = st.selectbox("Number of Dispatch Classes:", class_options)
    dispatch_breakpoint = st.selectbox("Dispatch Breakpoint:", breakpoint_options)
    custom_dispatch_breakpoint = None
    if dispatch_breakpoint == "Custom":
        custom_dispatch_breakpoint = st.text_input("Enter Custom Dispatch Breakpoints (comma-separated):")

    submitted = st.form_submit_button("Submit")

if submitted:
    st.success("Configuration saved!")

    summary_data = {
        "SIG": [sig_selection],
        "Fuel Model": [fuel_model],
        "RAWS Count": [number_of_raws],
        "Staffing Index": [staffing_index],
        "Staffing Breakpoint": [custom_staffing_breakpoint if custom_staffing_breakpoint else staffing_breakpoint],
        "Dispatch Index": [dispatch_index],
        "Dispatch Classes": [number_of_classes],
        "Dispatch Breakpoint": [custom_dispatch_breakpoint if custom_dispatch_breakpoint else dispatch_breakpoint]
    }
    summary_df = pd.DataFrame(summary_data)
    st.subheader("Dashboard Summary Table")
    st.dataframe(summary_df)

    st.subheader("Observed vs Forecast Graph from FEMS")

    try:
        response = requests.get(fems_url)
        fems_df = pd.read_csv(BytesIO(response.content))
        fems_df['sample_date'] = pd.to_datetime(fems_df['sample_date'])

        # Aggregate observed and forecast for plotting (dummy logic)
        observed = fems_df.groupby('sample_date')['index_value'].mean()
        forecast = observed.rolling(window=3, min_periods=1).mean() + 5

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(observed.index, observed.values, label="Observed", marker='o')
        ax.plot(forecast.index, forecast.values, label="Forecast", linestyle='--', marker='x')
        ax.fill_between(observed.index, 90, 97, color='red', alpha=0.1, label='90-97 Percentile')
        ax.fill_between(observed.index, 80, 95, color='orange', alpha=0.1, label='80-95 Percentile')

        ax.set_title("Observed and Forecast Index")
        ax.set_xlabel("Date")
        ax.set_ylabel("Index Value")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

        output_df = pd.DataFrame({
            "Date": observed.index,
            "Observed": observed.values,
            "Forecast": forecast.values
        })

        csv = output_df.to_csv(index=False).encode('utf-8')
        buffer = BytesIO()
        fig.savefig(buffer, format="png")
        image_bytes = buffer.getvalue()

        pdf_buffer = BytesIO()
        fig.savefig(pdf_buffer, format="pdf")
        pdf_bytes = pdf_buffer.getvalue()

        st.download_button("📥 Download Data as CSV", data=csv, file_name="sig_dashboard_output.csv", mime="text/csv")
        st.download_button("🖼️ Download Graph as Image", data=image_bytes, file_name="observed_forecast_graph.png", mime="image/png")
        st.download_button("📄 Download Graph as PDF", data=pdf_bytes, file_name="observed_forecast_graph.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Failed to load or process FEMS data: {e}")
