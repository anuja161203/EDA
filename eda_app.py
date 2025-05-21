import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="✈️ Flight Price EDA", layout="wide")
st.title("✈️ Interactive Flight Price Explorer")

# Load data
@st.cache_data

def load_data():
    train_df = pd.read_excel("Data_Train.xlsx")
    test_df = pd.read_excel("Test_set.xlsx")
    df = pd.concat([train_df, test_df], ignore_index=True)
    return df

final_df = load_data()

# Data Preprocessing
def preprocess_data(df):
    df['Date'] = df['Date_of_Journey'].str.split('/').str[0].astype(int)
    df['Month'] = df['Date_of_Journey'].str.split('/').str[1].astype(int)
    df['Year'] = df['Date_of_Journey'].str.split('/').str[2].astype(int)
    df.drop('Date_of_Journey', axis=1, inplace=True)

    df['Arrival_Time'] = df['Arrival_Time'].apply(lambda x: x.split(' ')[0])
    df['Arrival_hour'] = df['Arrival_Time'].str.split(':').str[0].astype(int)
    df['Arrival_min'] = df['Arrival_Time'].str.split(':').str[1].astype(int)
    df.drop('Arrival_Time', axis=1, inplace=True)

    df['Dept_hour'] = df['Dep_Time'].str.split(':').str[0].astype(int)
    df['Dept_min'] = df['Dep_Time'].str.split(':').str[1].astype(int)
    df.drop('Dep_Time', axis=1, inplace=True)

    df['Total_Stops'] = df['Total_Stops'].map({'non-stop':0,'1 stop':1,'2 stops':2,'3 stops':3,'4 stops':4})
    df.drop('Route', axis=1, inplace=True)

    df.dropna(inplace=True)

    df['duration_hour'] = df['Duration'].str.extract(r'(\d+)h').fillna(0).astype(int)
    df['duration_min'] = df['Duration'].str.extract(r'(\d+)m').fillna(0).astype(int)
    df.drop('Duration', axis=1, inplace=True)

    return df

final_df = preprocess_data(final_df)

# Sidebar filters
st.sidebar.header("📊 Filters")
airlines = st.sidebar.multiselect("Select Airline", final_df['Airline'].unique(), final_df['Airline'].unique())
sources = st.sidebar.multiselect("Select Source", final_df['Source'].unique(), final_df['Source'].unique())
stops = st.sidebar.multiselect("Select Stops", final_df['Total_Stops'].unique(), final_df['Total_Stops'].unique())

filtered_df = final_df[(final_df['Airline'].isin(airlines)) &
                       (final_df['Source'].isin(sources)) &
                       (final_df['Total_Stops'].isin(stops))]

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Overview", "💰 Price Analysis", "🕒 Time Analysis"])

with tab1:
    st.subheader("Flight Distribution")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(filtered_df, x='Airline', color='Airline', title="Flights by Airline")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(filtered_df, x='Source', color='Source', title="Flights by Source")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Price Comparison")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.box(filtered_df, x='Total_Stops', y='Price', color='Total_Stops', title="Price vs Stops")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        avg_price = filtered_df.groupby('Airline')['Price'].mean().reset_index()
        fig = px.bar(avg_price, x='Airline', y='Price', color='Airline', title="Avg Price per Airline")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Time vs Price")
    def duration_to_minutes(row):
        return row['duration_hour'] * 60 + row['duration_min']

    filtered_df['Duration_mins'] = filtered_df.apply(duration_to_minutes, axis=1)

    fig = px.scatter(filtered_df, x='Duration_mins', y='Price', color='Total_Stops',
                     title="Price vs Duration (mins)", hover_data=['Airline', 'Source', 'Destination'])
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🚀 Built with Streamlit | Interactive Dashboard by Anuja")
