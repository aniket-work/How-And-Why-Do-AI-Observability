import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import json
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="AI Agents for Observability Monitor", layout="wide")
st.title("AI Agents for Observability Usage Analytics")

# Initialize DB connection
conn = duckdb.connect('network_events.db')

# Add date filter
st.sidebar.header("Filters")
date_options = ["Last 24 hours", "Last 7 days", "Last 30 days", "All time"]
selected_date_range = st.sidebar.selectbox("Date Range", date_options)

# Convert selection to WHERE clause
date_filter = ""
if selected_date_range != "All time":
    days = {
        "Last 24 hours": 1,
        "Last 7 days": 7,
        "Last 30 days": 30
    }
    date_filter = f"WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '{days[selected_date_range]}' DAY"

# Create 2x2 layout
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Model Usage Distribution
with col1:
    st.subheader("Model Usage Distribution")
    query = f"""
    SELECT 
        model,
        COUNT(*) as count,
        AVG(total_tokens) as avg_tokens
    FROM openai_records_a1e208f2
    {date_filter}
    GROUP BY model
    ORDER BY count DESC
    """
    df = pd.DataFrame(conn.execute(query).fetchall(), columns=['model', 'count', 'avg_tokens'])
    if not df.empty:
        fig = px.pie(df, values='count', names='model', title='Requests by Model')
        st.plotly_chart(fig, use_container_width=True)

# Token Usage Trends
with col2:
    st.subheader("Token Usage Analysis")
    query = f"""
    SELECT 
        DATE_TRUNC('hour', timestamp) as hour,
        SUM(prompt_tokens) as prompt_tokens,
        SUM(completion_tokens) as completion_tokens
    FROM openai_records_a1e208f2
    {date_filter}
    GROUP BY 1
    ORDER BY 1
    """
    df = pd.DataFrame(conn.execute(query).fetchall(),
                     columns=['hour', 'prompt_tokens', 'completion_tokens'])
    if not df.empty:
        fig = px.line(df, x='hour',
                     y=['prompt_tokens', 'completion_tokens'],
                     title='Token Usage Over Time')
        st.plotly_chart(fig, use_container_width=True)

# Error Analysis
with col3:
    st.subheader("Error Analysis")
    query = f"""
    SELECT 
        CASE 
            WHEN error IS NULL THEN 'Success'
            ELSE 'Error'
        END as status,
        COUNT(*) as count
    FROM openai_records_a1e208f2
    {date_filter}
    GROUP BY 1
    """
    df = pd.DataFrame(conn.execute(query).fetchall(), columns=['status', 'count'])
    if not df.empty:
        fig = px.bar(df, x='status', y='count', color='status',
                    title='Request Success vs Errors')
        st.plotly_chart(fig, use_container_width=True)

# Function Usage
with col4:
    st.subheader("Function Call Distribution")
    query = f"""
    SELECT 
        CASE 
            WHEN function_call IS NOT NULL THEN 'With Function Calls'
            ELSE 'Without Function Calls'
        END as function_usage,
        COUNT(*) as count
    FROM openai_records_a1e208f2
    {date_filter}
    GROUP BY 1
    """
    df = pd.DataFrame(conn.execute(query).fetchall(), columns=['function_usage', 'count'])
    if not df.empty:
        fig = px.pie(df, values='count', names='function_usage',
                    title='Requests with Function Calls')
        st.plotly_chart(fig, use_container_width=True)

# Key Metrics
st.subheader("Key Metrics")
col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)

with col_metrics1:
    query = f"""
    SELECT COUNT(*) as total_requests
    FROM openai_records_a1e208f2
    {date_filter}
    """
    total_requests = conn.execute(query).fetchone()[0]
    st.metric("Total Requests", f"{total_requests:,}")

with col_metrics2:
    query = f"""
    SELECT SUM(total_tokens) as total_tokens
    FROM openai_records_a1e208f2
    {date_filter}
    """
    total_tokens = conn.execute(query).fetchone()[0]
    st.metric("Total Tokens Used", f"{total_tokens:,}")

with col_metrics3:
    query = f"""
    SELECT COUNT(DISTINCT model) as unique_models
    FROM openai_records_a1e208f2
    {date_filter}
    """
    unique_models = conn.execute(query).fetchone()[0]
    st.metric("Unique Models", unique_models)

with col_metrics4:
    query = f"""
    SELECT AVG(total_tokens) as avg_tokens_per_request
    FROM openai_records_a1e208f2
    {date_filter}
    """
    avg_tokens = conn.execute(query).fetchone()[0]
    st.metric("Avg Tokens/Request", f"{avg_tokens:.1f}")

# Recent Requests Table
st.subheader("Recent Requests")
query = f"""
SELECT 
    timestamp,
    model,
    prompt_tokens,
    completion_tokens,
    total_tokens,
    finish_reason,
    CASE WHEN error IS NULL THEN 'Success' ELSE error END as status
FROM openai_records_a1e208f2
{date_filter}
ORDER BY timestamp DESC
LIMIT 10
"""
df = pd.DataFrame(conn.execute(query).fetchall(),
                 columns=['timestamp', 'model', 'prompt_tokens', 'completion_tokens',
                         'total_tokens', 'finish_reason', 'status'])
st.dataframe(df, use_container_width=True)

# Add refresh button
if st.button('Refresh Data'):
    st.experimental_rerun()