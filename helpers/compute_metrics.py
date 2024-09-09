import streamlit as st

# Function to create a custom metric with border
def custom_metric(label, value, delta= None):
    st.markdown("""
    <style>
        .metric-container {
            border: 3px solid #f2c464;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 5px;
        }
        .metric-label {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .metric-delta {
            color: #28a745;
            font-size: 14px;
        }
    </style>
    """, unsafe_allow_html=True)
    #  <div class="metric-delta">↑ {delta}</div>
    return f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    
    </div>
    """

    
CLUSTER_NAMES = [
    'Loyal High Spenders', 
    'At-Risk Low Spenders', 
    'Top VIPs', 
    'New or Infrequent Shoppers', 
    'Occasional Bargain Seekers'
]
