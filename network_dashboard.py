# Save this exactly as dashboard.py

import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

# Set page config
st.set_page_config(page_title="Network Monitor", layout="wide")
st.title("Network Security Monitor")

# Initialize DB connection
conn = duckdb.connect('network_events.db')

# Create 2x2 layout
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Event Types Chart
with col1:
    st.subheader("Event Types")
    query = """
    SELECT 
        JSON_EXTRACT(messages, '$[0].content')::json->>'event_type' as event_type,
        COUNT(*) as count
    FROM openai_records_98508683
    WHERE JSON_EXTRACT(messages, '$[0].content') IS NOT NULL
    GROUP BY 1
    """
    df = pd.DataFrame(conn.execute(query).fetchall(), columns=['event_type', 'count'])
    if not df.empty:
        fig = px.pie(df, values='count', names='event_type')
        st.plotly_chart(fig, use_container_width=True)

# Risk Levels
with col2:
    st.subheader("Risk Levels")
    query = """
    SELECT 
        JSON_EXTRACT(messages, '$[0].content')::json->>'risk_level' as risk_level,
        COUNT(*) as count
    FROM openai_records_98508683
    WHERE JSON_EXTRACT(messages, '$[0].content') IS NOT NULL
    GROUP BY 1
    """
    df = pd.DataFrame(conn.execute(query).fetchall(), columns=['risk_level', 'count'])
    if not df.empty:
        fig = px.bar(df, x='risk_level', y='count', color='risk_level')
        st.plotly_chart(fig, use_container_width=True)

# Protocols
with col3:
    st.subheader("Protocols")
    query = """
    SELECT 
        JSON_EXTRACT(messages, '$[0].content')::json->>'protocol' as protocol,
        COUNT(*) as count
    FROM openai_records_98508683
    WHERE JSON_EXTRACT(messages, '$[0].content') IS NOT NULL
    GROUP BY 1
    """
    df = pd.DataFrame(conn.execute(query).fetchall(), columns=['protocol', 'count'])
    if not df.empty:
        fig = px.bar(df, x='protocol', y='count')
        st.plotly_chart(fig, use_container_width=True)

# Timeline
with col4:
    st.subheader("Events Timeline")
    query = """
    SELECT 
        timestamp,
        COUNT(*) as count
    FROM openai_records_98508683
    GROUP BY timestamp
    ORDER BY timestamp
    """
    df = pd.DataFrame(conn.execute(query).fetchall(), columns=['timestamp', 'count'])
    if not df.empty:
        fig = px.line(df, x='timestamp', y='count')
        st.plotly_chart(fig, use_container_width=True)

# Recent Events Table
st.subheader("Recent Events")
query = """
SELECT 
    timestamp,
    JSON_EXTRACT(messages, '$[0].content')::json->>'event_type' as event_type,
    JSON_EXTRACT(messages, '$[0].content')::json->>'risk_level' as risk_level,
    JSON_EXTRACT(messages, '$[0].content')::json->>'protocol' as protocol
FROM openai_records_98508683
ORDER BY timestamp DESC
LIMIT 10
"""
df = pd.DataFrame(conn.execute(query).fetchall(),
                 columns=['timestamp', 'event_type', 'risk_level', 'protocol'])
st.dataframe(df, use_container_width=True)

# Add refresh button
if st.button('Refresh Data'):
    st.experimental_rerun()
