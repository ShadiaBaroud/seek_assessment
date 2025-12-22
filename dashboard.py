# dashboard.py

import streamlit as st
import requests
import json
import pandas as pd

# Define the local API endpoint
API_URL = "http://api:8000/analyze"

st.set_page_config(layout="wide", page_title="Traffic Analysis Dashboard")

st.title("🚗 SEEK Traffic Counter Analysis")
st.subheader("Data processed by FastAPI Microservice")

# File uploader widget in Streamlit
uploaded_file = st.file_uploader("Upload your traffic file (sample.txt):", type=["txt"])

if uploaded_file is not None:
    with st.spinner("Processing file through FastAPI service..."):
        try:
            # 1. Prepare the file for the POST request
            files = {"file": uploaded_file.getvalue()}
            
            # 2. Call the FastAPI endpoint
            response = requests.post(API_URL, files=files)
            
            # Raise exception for bad status codes (e.g., 500 from FastAPI)
            response.raise_for_status()
            
            # Get the structured JSON analysis
            data = response.json().get("analysis", {})

            st.success(f"Analysis complete! Total records processed: {response.json().get('meta', {}).get('records_processed')}")

            # --- Display Results ---

            col1, col2 = st.columns(2)

            with col1:
                st.metric(label="Total Cars Recorded", value=data.get("total_cars"))

                # Convert daily counts to a DataFrame for clean display
                daily_df = pd.DataFrame(data.get("cars_per_day", {}).items(), columns=['Date', 'Total Cars'])
                daily_df['Date'] = pd.to_datetime(daily_df['Date'])
                st.write("### Cars Per Day (Chronological)")
                st.dataframe(daily_df.set_index('Date'))
                
            with col2:
                st.write("### Top 3 Half-Hour Periods (Highest Traffic)")
                # Convert top 3 to DataFrame
                top3_df = pd.DataFrame(data.get("top_3_periods", []))
                top3_df['timestamp'] = pd.to_datetime(top3_df['timestamp'])
                st.dataframe(top3_df)
                st.bar_chart(top3_df.set_index('timestamp')['count'])

            st.markdown("---")

            st.write("### 1.5 Hour Period with Lowest Traffic (3 Contiguous Records)")
            low_window_df = pd.DataFrame(data.get("lowest_1_5_hour_window", []))
            low_window_df['timestamp'] = pd.to_datetime(low_window_df['timestamp'])
            st.dataframe(low_window_df)
            
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Is your FastAPI server running? Please run: uvicorn api:app --reload")
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")