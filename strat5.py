import streamlit as st
import pandas as pd
import math

# Constants
DATA_FILE_BASE_PATH = './Data/cluster_calculation/hashed/'
CLUSTER_NAMES = [
    'Loyal High Spenders', 
    'At-Risk Low Spenders', 
    'Top VIPs', 
    'New or Infrequent Shoppers', 
    'Occasional Bargain Seekers'
]

def load_data(selected_cluster):
    data_file_path = f"{DATA_FILE_BASE_PATH}rfm_cluster_{selected_cluster}.csv"
    return pd.read_csv(data_file_path)

def get_cluster_statistics(selected_cluster):
    path = f'{DATA_FILE_BASE_PATH}Full Dataset of Cluster {selected_cluster}.csv'
    df = pd.read_csv(path)
    
    grouped = df.groupby('cardholder_id').agg(
        Total_Transaction_Value=('transaction_amount', 'sum'),
        Total_Cashback_Value=('cashback_amount', 'sum'),
        Transaction_Count=('transaction_amount', 'count')
    ).reset_index()

    grouped['Avg_Transaction_Value'] = grouped['Total_Transaction_Value'] / grouped['Transaction_Count']
    grouped['Avg_Cashback_Value'] = grouped['Total_Cashback_Value'] / grouped['Transaction_Count']

    avg_order = grouped['Avg_Transaction_Value'].mean()
    avg_cashback = grouped['Avg_Cashback_Value'].mean()

    return {
        'avg_order': math.floor(avg_order),
        'avg_cashback': math.floor(avg_cashback),
        'cardholder_count': grouped['cardholder_id'].nunique()
    }

def calculate_cashback_budget_and_customers(revenue_target, avg_order, avg_cashback, num_users):
    potential_cashback_budget = avg_cashback * num_users
    max_possible_revenue = avg_order * num_users
    
    if revenue_target < potential_cashback_budget:
        return None, f"Error: The revenue target must be at least {math.floor(potential_cashback_budget)} ¥ to cover the minimum cashback budget."
    
    num_customers_to_target = min(revenue_target / avg_order, num_users)
    cashback_budget_needed = num_customers_to_target * avg_cashback
    
    if num_customers_to_target == num_users and revenue_target > max_possible_revenue:
        return None, f"Error: The revenue target of {revenue_target} ¥ exceeds the maximum possible revenue ({math.floor(max_possible_revenue)} ¥) that can be generated from this cluster."
    
    return cashback_budget_needed, num_customers_to_target

def display_cluster_summary(cluster_stats, df):
    st.subheader(f"Cluster Summary Statistics")
    st.write(f"Number of Users: {cluster_stats['cardholder_count']}")
    st.write(f"Average Recency: {math.ceil(df['Recency'].mean())} days")
    st.write(f"Average Frequency: {math.ceil(df['Frequency'].mean())} transactions")
    st.write(f"Average Order Value: {cluster_stats['avg_order']:.2f} ¥")
    st.write(f"Average Monetary Value: {math.floor(df['Monetary'].mean()):.2f} ¥")
    st.write(f"Average Cashback per User: {cluster_stats['avg_cashback']:.2f} ¥")

def display_results(revenue_target, cashback_budget, num_customers, df, prefix=""):
    st.write(f"**To achieve a revenue target of** {math.floor(revenue_target):,.0f} ¥:")
    st.success(f"**{prefix}Cashback Budget Needed:** {math.floor(cashback_budget):,.0f} ¥")
    st.success(f"**{prefix}Number of Customers to Target:** {math.ceil(num_customers):,.0f} customers")
    
    top_customers = df.sort_values('Monetary', ascending=False).head(math.ceil(num_customers)).reset_index(drop=True)
    
    st.subheader(f"{prefix}Top Customers Preview")
    st.dataframe(top_customers)
    
    st.download_button(
        label=f"📥 Download {prefix}Top Customer Data as CSV",
        data=top_customers.to_csv(index=True).encode('utf-8'),
        file_name=f'{prefix.lower()}top_customers_cluster_{st.session_state.selected_cluster}.csv',
        mime='text/csv',
        key=f"download_{prefix.lower()}"
    )

def render_sliders_and_results(avg_cashback, avg_order, initial_num_customers, initial_cashback_budget, df):
    if 'adjusted_num_customers' not in st.session_state:
        st.session_state.adjusted_num_customers = int(math.ceil(initial_num_customers))
    if 'adjusted_cashback_amount' not in st.session_state:
        st.session_state.adjusted_cashback_amount = initial_cashback_budget

    st.markdown("---")
    st.subheader("Adjust Parameters")

    adjusted_num_customers = st.slider(
        "Adjust the number of customers to target:",
        min_value=1,
        max_value=int(math.ceil(initial_num_customers)),
        value=st.session_state.adjusted_num_customers,
        key="slider_num_customers"
    )
    
    st.session_state.adjusted_num_customers = adjusted_num_customers

    adjusted_cashback_budget = math.floor(adjusted_num_customers * avg_cashback)
    adjusted_target_revenue = math.floor(adjusted_num_customers * avg_order)

    display_results(adjusted_target_revenue, adjusted_cashback_budget, adjusted_num_customers, df, prefix="Adjusted ")

    st.markdown("---")

    adjusted_cashback_amount = st.slider(
        "Adjust the cashback amount (total):",
        min_value=0.0,
        max_value=initial_cashback_budget,
        value=st.session_state.adjusted_cashback_amount,
        key="slider_cashback_amount"
    )
    st.session_state.adjusted_cashback_amount = adjusted_cashback_amount

    final_num_customers = math.ceil(adjusted_cashback_amount / avg_cashback)
    final_target_revenue = math.floor(final_num_customers * avg_order)

    display_results(final_target_revenue, adjusted_cashback_amount, final_num_customers, df, prefix="Final ")

def render():
    st.image("./Data/assets/logo.png", width=200)
    st.title("Cashback Budget Calculator")

    if 'selected_cluster' not in st.session_state:
        st.session_state.selected_cluster = None
    if 'revenue_target' not in st.session_state:
        st.session_state.revenue_target = 1000000
    if 'calculation_done' not in st.session_state:
        st.session_state.calculation_done = False
    
    st.markdown("""
    <style>
    button[kind="secondary"] {
        min-height: auto;
        padding: 10px;
        font-size: 16px;
        width: 100%;
        height: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            if st.button(CLUSTER_NAMES[i]):
                st.session_state.selected_cluster = i
                st.session_state.revenue_target = 1000000  # Reset revenue target when cluster changes
                st.session_state.calculation_done = False
                if 'adjusted_num_customers' in st.session_state:
                    del st.session_state.adjusted_num_customers
                if 'adjusted_cashback_amount' in st.session_state:
                    del st.session_state.adjusted_cashback_amount

    if st.session_state.selected_cluster is None:
        return

    st.markdown(f"<h4>Selected Cluster: {CLUSTER_NAMES[st.session_state.selected_cluster]}</h4>", unsafe_allow_html=True)

    df = load_data(st.session_state.selected_cluster)
    cluster_stats = get_cluster_statistics(st.session_state.selected_cluster)

    with st.expander("Summary Statistics of the cluster"):
        display_cluster_summary(cluster_stats, df)

    st.markdown("---")
    st.session_state.revenue_target = st.number_input("Enter your Revenue Target (in ¥):", min_value=0, step=10000, value=st.session_state.revenue_target)
    
    result = calculate_cashback_budget_and_customers(st.session_state.revenue_target, cluster_stats['avg_order'], cluster_stats['avg_cashback'], cluster_stats['cardholder_count'])
    
    if isinstance(result[0], float):
        cashback_budget, num_customers = result
        display_results(st.session_state.revenue_target, cashback_budget, num_customers, df, prefix="Initial ")
        st.session_state.calculation_done = True
    else:
        st.error(result[1])
        st.session_state.calculation_done = False

    if st.session_state.calculation_done:
        render_sliders_and_results(cluster_stats['avg_cashback'], cluster_stats['avg_order'], num_customers, cashback_budget, df)

# if __name__ == "__main__":
#     render()