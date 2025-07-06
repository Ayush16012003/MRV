import streamlit as st
import pandas as pd
import os
import plotly.express as px

# File name
DATA_FILE = "data.csv"

# GWP lookup
GWP_MAP = {
    "R-134a": 1430,
    "R-410A": 2088,
    "R-404A": 3922,
    "R-22": 1810,
    "R-1234yf": 1,
    "R-290": 3
}

# Load or create data file
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Date", "Refrigerant", "Weight (kg)", "GWP", "CO2e (kg)"])
    df.to_csv(DATA_FILE, index=False)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["📥 Data Entry", "📊 Dashboard"])

# Page: Data Entry
if page == "📥 Data Entry":
    st.title("♻️ Refrigerant Recovery - Data Entry")

    with st.form("entry_form"):
        date = st.date_input("Date of Recovery")
        refrigerant = st.selectbox("Refrigerant Type", list(GWP_MAP.keys()))
        weight = st.number_input("Weight Recovered (kg)", min_value=0.0, step=0.1)

        submit = st.form_submit_button("Submit")

        if submit:
            gwp = GWP_MAP[refrigerant]
            co2e = weight * gwp

            new_row = pd.DataFrame([{
                "Date": date,
                "Refrigerant": refrigerant,
                "Weight (kg)": weight,
                "GWP": gwp,
                "CO2e (kg)": co2e
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)

            st.success(f"✅ Entry saved! CO₂e = {co2e:.2f} kg")

# Page: Dashboard
if page == "📊 Dashboard":
    st.title("📊 Refrigerant Recovery Dashboard")

    if df.empty:
        st.warning("No data available yet. Please add entries from the Data Entry page.")
    else:
        total_weight = df["Weight (kg)"].sum()
        total_co2e = df["CO2e (kg)"].sum()
        total_credits = total_co2e / 1000

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Refrigerant (kg)", f"{total_weight:.2f}")
        col2.metric("CO₂e Avoided (kg)", f"{total_co2e:,.2f}")
        col3.metric("Carbon Credits Earned", f"{total_credits:.2f}")

        st.divider()

        st.subheader("🧊 CO₂e by Refrigerant Type")
        co2e_by_type = df.groupby("Refrigerant")["CO2e (kg)"].sum().reset_index()
        fig_bar = px.bar(co2e_by_type, x="Refrigerant", y="CO2e (kg)", color="Refrigerant")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📦 Weight Distribution by Refrigerant")
        weight_by_type = df.groupby("Refrigerant")["Weight (kg)"].sum().reset_index()
        fig_pie = px.pie(weight_by_type, names="Refrigerant", values="Weight (kg)")
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("📋 All Entries")
        st.dataframe(df)
