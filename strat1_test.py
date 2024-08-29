import streamlit as st
import pandas as pd
import math

# Base path for data files
data_file_base_path = './Data/cluster_calculation/hashed/'

def render():
    st.image("./Data/assets/logo.png", width=200)  # Add your company logo here
    st.title("Cashback Budget Calculator")

    if 'selected_cluster' not in st.session_state:
        st.session_state.selected_cluster = None
    cluster_names = [
        'Loyal High Spenders', 
        'At-Risk Low Spenders', 
        'Top VIPs', 
        'New or Infrequent Shoppers', 
        'Occasional Bargain Seekers'
    ]
    
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

    selected_cluster = None

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button(cluster_names[0]):
            st.session_state.selected_cluster = 0

    with col2:
        if st.button(cluster_names[1]):
            st.session_state.selected_cluster = 1

    with col3:
        if st.button(cluster_names[2]):
            st.session_state.selected_cluster = 2

    with col4:
        if st.button(cluster_names[3]):
            st.session_state.selected_cluster = 3

    with col5:
        if st.button(cluster_names[4]):
            st.session_state.selected_cluster = 4

    selected_cluster = st.session_state.selected_cluster

    if selected_cluster is None:
        return

    data_file_path = f"{data_file_base_path}rfm_cluster_{selected_cluster}.csv"
    
    avg_order_rounded, avg_cashback_rounded, cardholder_count = get_man_values(selected_cluster)
    df = pd.read_csv(data_file_path)
    mean_monetary = avg_order_rounded
    avg_cashback = avg_cashback_rounded
    num_users = cardholder_count

    st.markdown(f"<h4>Selected Cluster: {cluster_names[selected_cluster]}</h4>", unsafe_allow_html=True)

    recency = math.ceil(df['Recency'].mean())
    frequency = math.ceil(df['Frequency'].mean())
    monetory = math.floor(df['Monetary'].mean())

    with st.expander(f"Summary Statistics of the cluster"):
        st.subheader(f"Cluster {cluster_names[selected_cluster]} Summary Statistics")
        st.write(f"Number of Users: {num_users}")
        st.write(f"Average Recency: {recency} days")
        st.write(f"Average Frequency: {frequency} transactions")
        st.write(f"Average Order Value: {mean_monetary:.2f} ¥")
        st.write(f"Average Monetary Value: {monetory:.2f} ¥")
        st.write(f"Average Cashback per User: {avg_cashback:.2f} ¥")

    def calculate_cashback_budget_and_customers(revenue_target):
        potential_cashback_budget = avg_cashback * num_users
        max_possible_revenue = mean_monetary * num_users
        if revenue_target < potential_cashback_budget:
            return None, f"Error: The revenue target must be at least {math.floor(potential_cashback_budget)} ¥ to cover the minimum cashback budget."
        num_customers_to_target = min(revenue_target / mean_monetary, num_users)
        cashback_budget_needed = num_customers_to_target * avg_cashback
        if num_customers_to_target == num_users and revenue_target > max_possible_revenue:
            return None, f"Error: The revenue target of {revenue_target} ¥ exceeds the maximum possible revenue ({math.floor(max_possible_revenue)} ¥) that can be generated from this cluster."
        return cashback_budget_needed, num_customers_to_target

    if 'revenue_target' not in st.session_state:    
        st.session_state.revenue_target = 1000000
        st.session_state.calculated = False
        st.session_state.cashback_budget = None
        st.session_state.num_customers = None
        st.session_state.error = None
        st.session_state.show_summary = False 

    st.markdown("---")
    revenue_target = st.number_input("Enter your Revenue Target (in ¥):", min_value=0, step=10000, value=1000000)
    
    if revenue_target != st.session_state.revenue_target:
        st.session_state.revenue_target = revenue_target
        st.session_state.calculated = False
        st.session_state.cashback_budget = None
        st.session_state.num_customers = None
        st.session_state.error = None
    
    if st.button("Calculate Cashback Budget", type="primary") or st.session_state.calculated:
        st.session_state.calculated = False
        if not st.session_state.calculated:
            result, error = calculate_cashback_budget_and_customers(revenue_target)
            if result:
                st.session_state.cashback_budget, st.session_state.num_customers = result, error
                st.session_state.error = None
                st.session_state.calculated = True
            else:
                st.session_state.error = error
                st.session_state.calculated = True
        
        if st.session_state.error:
            st.error(st.session_state.error)
        else:
            cashback_budget, num_customers = st.session_state.cashback_budget, st.session_state.num_customers
            st.write(f"**To achieve a revenue target of**  {math.floor(revenue_target):,.0f} ¥:")
            st.success(f"**Cashback Budget Needed:** {math.floor(cashback_budget):,.0f} ¥")
            st.success(f"**Number of Customers to Target:** {math.ceil(num_customers):,.0f} customers")
            
            df = pd.read_csv(data_file_path)
            top_customers = df.head(math.ceil(num_customers))
            top_customers = top_customers.reset_index(drop=True)

            st.subheader("Top Customers Preview")
            st.dataframe(top_customers)

            st.download_button(
                label="📥 Download Top Customer Data as CSV",
                data=top_customers.to_csv(index=True).encode('utf-8'),
                file_name=f'top_customers_cluster_{selected_cluster}.csv',
                mime='text/csv'
            )
            
            if st.checkbox("Show and Adjust Sliders"):
                adjusted_num_customers = st.slider("Adjust the number of customers to target:",
                                                min_value=1, max_value=int(math.ceil(num_customers)), value=int(math.ceil(num_customers)))
                adjusted_cashback_budget = math.floor(adjusted_num_customers * avg_cashback)
                adjusted_target_revenue = math.floor(adjusted_num_customers * mean_monetary)
                st.success(f"**Adjusted Cashback Budget:** {adjusted_cashback_budget:,.0f} ¥")
                st.success(f"**Adjusted Target Revenue:** {adjusted_target_revenue:,.0f} ¥")
                
                df_sorted = df.sort_values(by='Monetary', ascending=False)
                top_customers = df_sorted.head(int(adjusted_num_customers))
                top_customers = top_customers.reset_index(drop=True)

                st.subheader("Adjusted Top Customers Preview")
                st.dataframe(top_customers)
                
                st.download_button(
                    label="Download Top Customer Data as CSV",
                    data=top_customers.to_csv(index=True).encode('utf-8'),
                    file_name=f'top_customers_cluster_{selected_cluster}.csv',
                    mime='text/csv',
                    key="download_selected"
                )
                
                st.markdown("---")
                
                adjusted_cashback_amount = st.slider("Adjust the cashback amount (total):",
                                                    min_value=0.0, max_value=cashback_budget, value=cashback_budget)
                final_num_customers = math.ceil(adjusted_cashback_amount / avg_cashback)
                final_target_revenue = math.floor(final_num_customers * mean_monetary)
                st.success(f"**Final Number of Customers to Target:**  {final_num_customers:.0f} customers")
                st.success(f"**Final Adjusted Target Revenue:** {final_target_revenue:,.0f} ¥")
                
                df_sorted = df.sort_values('Monetary', ascending=False)
                top_customers = df_sorted.head(int(final_num_customers))
                top_customers = top_customers.reset_index(drop=True)
                
                st.subheader("Final Adjusted Top Customers Preview")
                st.dataframe(top_customers)

                st.download_button(
                    label="Download Top Customer Data as CSV",
                    data=top_customers.to_csv(index=True).encode('utf-8'),
                    file_name=f'top_customers_cluster_{selected_cluster}.csv',
                    mime='text/csv',
                    key="button_cashback"
                )
    

def get_man_values(selected_cluster):
    path = f'./Data/cluster_calculation/hashed/Full Dataset of Cluster {selected_cluster}.csv'
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

    avg_order_rounded = math.floor(avg_order)
    avg_cashback_rounded = math.floor(avg_cashback)
    cardholder_count = grouped['cardholder_id'].nunique()

    return avg_order_rounded, avg_cashback_rounded, cardholder_count