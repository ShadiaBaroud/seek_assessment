# dashboard.py

import os
import streamlit as st
import requests
import pandas as pd

# -------------------------------------------------------------------
# API configuration
# -------------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
API_URL = f"{API_BASE_URL}/analyze"

# -------------------------------------------------------------------
# Streamlit page config
# -------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Traffic Analysis Dashboard")

st.title("🚗 SEEK Traffic Counter Analysis")
st.subheader("Data processed by FastAPI Microservice")

# -------------------------------------------------------------------
# File uploader
# -------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload your traffic file (sample.txt):",
    type=["txt"],
)

if uploaded_file is not None:
    with st.spinner("Processing file through FastAPI service..."):
        try:
            # Prepare multipart file correctly for FastAPI
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "text/plain",
                )
            }

            response = requests.post(API_URL, files=files)
            response.raise_for_status()

            result = response.json()

            # Debug helper (optional – can remove later)
            # st.json(result)

            st.success("Analysis complete!")

            # -------------------------------------------------------------------
            # Display results
            # -------------------------------------------------------------------
            col1, col2 = st.columns(2)

            # ---------------- LEFT COLUMN ----------------
            with col1:
                st.metric(
                    label="Total Cars Recorded",
                    value=result["total_count"],
                )

                st.write("### Cars Per Day (Chronological)")
                daily_df = pd.DataFrame(
                    result["daily_counts"].items(),
                    columns=["Date", "Total Cars"],
                )
                daily_df["Date"] = pd.to_datetime(daily_df["Date"])
                st.dataframe(daily_df.sort_values("Date").set_index("Date"))

            # ---------------- RIGHT COLUMN ----------------
            with col2:
                st.write("### Top 3 Half-Hour Periods (Highest Traffic)")
                top3_df = pd.DataFrame(result["top_periods"])
                top3_df["timestamp"] = pd.to_datetime(top3_df["timestamp"])
                st.dataframe(top3_df)

                st.bar_chart(
                    top3_df.set_index("timestamp")["count"]
                )

            st.markdown("---")

            # ---------------- LOWEST WINDOW ----------------
            st.write("### Lowest 1.5-Hour Window (3 Contiguous Records)")
            lw = result["lowest_window"]

            st.write(f"**Start:** {lw['start']}")
            st.write(f"**End:** {lw['end']}")
            st.write(f"**Total Cars:** {lw['total_count']}")

        except requests.exceptions.ConnectionError:
            st.error(
                "Connection Error: Unable to reach FastAPI service. "
                "Ensure the API container is running."
            )
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
