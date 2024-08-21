import streamlit as st
import pandas as pd

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

    # Initialize the selected cluster
    selected_cluster = None
 
    # Create columns for buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Display buttons in each column
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
    # st.write("Selected cluster:", cluster_names[selected_cluster] if selected_cluster is not None else "None")

    if selected_cluster is None:
        return
    data_file_path = f"{data_file_base_path}rfm_cluster_{selected_cluster}.csv"

    # Dummy values for mean_monetary, avg_cashback, and num_users
    # df['Monetary'] = df['Monetary'].mean()
    # mean_monetary = 2001.3
    
    avg_order_rounded, avg_cashback_rounded, cardholder_count = get_man_values(selected_cluster);
    df = pd.read_csv(data_file_path )
    mean_monetary = avg_order_rounded
    # print("mean_monetary",mean_monetary)
    avg_cashback = avg_cashback_rounded
    # num_users = 3258
    num_users = cardholder_count
    # print("num_users",num_users)

    st.markdown(f"<h4>Selected Cluster: {cluster_names[selected_cluster]}</h4>", unsafe_allow_html=True)

        # Button to toggle Cluster Summary Statistics visibility
    with st.expander(f"Summary Statistics of the cluster"):
        st.subheader(f"Cluster {cluster_names[selected_cluster]} Summary Statistics")
        st.write(f"Number of Users: {num_users}")
        st.write(f"Average Recency: {36.97:.2f} days")
        st.write(f"Average Frequency: {1.43:.2f} transactions")
        st.write(f"Average Monetary Value: {mean_monetary:.2f} yen")
        st.write(f"Average Cashback per User: {avg_cashback:.2f} yen")



    # Function to calculate cashback budget and customers to target
    def calculate_cashback_budget_and_customers(revenue_target):
        print("mean_monetary from cluster",mean_monetary)
        potential_cashback_budget = avg_cashback * num_users
        max_possible_revenue = mean_monetary * num_users
        if revenue_target < potential_cashback_budget:
            return None, f"Error: The revenue target must be at least {potential_cashback_budget:.2f} yen to cover the minimum cashback budget."
        num_customers_to_target = min(revenue_target / mean_monetary, num_users)
        cashback_budget_needed = num_customers_to_target * avg_cashback
        if num_customers_to_target == num_users and revenue_target > max_possible_revenue:
            return None, f"Error: The revenue target of {revenue_target} yen exceeds the maximum possible revenue ({max_possible_revenue:.2f} yen) that can be generated from this cluster."
        return cashback_budget_needed, num_customers_to_target


    
    # Initialize session state
    if 'revenue_target' not in st.session_state:    
        st.session_state.revenue_target = 1000000
        st.session_state.calculated = False
        st.session_state.cashback_budget = None
        st.session_state.num_customers = None
        st.session_state.error = None
        st.session_state.show_summary = False 
    
    st.markdown("---")
    # Input: Revenue target
    revenue_target = st.number_input("Enter your Revenue Target (in yen):", min_value=0, step=10000, value=1000000)
    
    
    # Check if the revenue target has changed
    if revenue_target != st.session_state.revenue_target:
        st.session_state.revenue_target = revenue_target
        st.session_state.calculated = False
        st.session_state.cashback_budget = None
        st.session_state.num_customers = None
        st.session_state.error = None
    
    # Calculate and display results
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
            st.write(f"**To achieve a revenue target of**  {revenue_target:,.0f} yen:")
            st.success(f"**Cashback Budget Needed:** {cashback_budget:,.0f} yen")
            st.success(f"**Number of Customers to Target:** {num_customers:,.0f} customers")
            
            df = pd.read_csv(data_file_path)

            top_customers = df.head(round(num_customers))
            top_customers = top_customers.reset_index(drop=True)

            # Preview the top customers dataset
            st.subheader("Top Customers Preview")
            st.dataframe(top_customers)

            st.download_button(
                label="📥 Download Top Customer Data as CSV",
                data=top_customers.to_csv(index=True).encode('utf-8'),
                file_name=f'top_customers_cluster_{selected_cluster}.csv',
                mime='text/csv'
            )
            
            # Add a checkbox to show or hide the sliders
            if st.checkbox("Show and Adjust Sliders"):
                # User adjustment of number of customers to target
                adjusted_num_customers = st.slider("Adjust the number of customers to target:",
                                                min_value=1, max_value=int(num_customers), value=int(num_customers))
                # Recalculate based on adjusted number of customers
                adjusted_cashback_budget = adjusted_num_customers * avg_cashback
                adjusted_target_revenue = adjusted_num_customers * mean_monetary
                st.success(f"**Adjusted Cashback Budget:** {adjusted_cashback_budget:,.0f} yen")
                st.success(f"**Adjusted Target Revenue:** {adjusted_target_revenue:,.0f} yen")
                
                df_sorted = df.sort_values(by='Monetary', ascending=False)
                # Select top customers based on final_num_customers
                top_customers = df_sorted.head(int(adjusted_num_customers))
                top_customers = top_customers.reset_index(drop=True)

                # Preview the adjusted top customers dataset
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
                
                # User adjustment of cashback amount
                adjusted_cashback_amount = st.slider("Adjust the cashback amount (total):",
                                                    min_value=0.0, max_value=cashback_budget, value=cashback_budget)
                # Recalculate based on adjusted cashback amount
                final_num_customers = adjusted_cashback_amount / avg_cashback
                final_target_revenue = final_num_customers * mean_monetary
                st.success(f"**Final Number of Customers to Target:**  {final_num_customers:.0f} customers")
                st.success(f"**Final Adjusted Target Revenue:** {final_target_revenue:,.0f} yen")
                
                # Sort by Monetary value in descending order
                df_sorted = df.sort_values('Monetary', ascending=False)
                # Select top customers based on final_num_customers
                top_customers = df_sorted.head(int(final_num_customers))
                top_customers = top_customers.reset_index(drop=True)
                
                # Preview the final adjusted top customers dataset
                st.subheader("Final Adjusted Top Customers Preview")
                st.dataframe(top_customers)

                # Option to download the data as a CSV file
                st.download_button(
                    label="Download Top Customer Data as CSV",
                    data=top_customers.to_csv(index=True).encode('utf-8'),
                    file_name=f'top_customers_cluster_{selected_cluster}.csv',
                    mime='text/csv',
                    key="button_cashback"
                )
    


def get_man_values(selected_cluster):
    # print("calculating from the cluster: ", selected_cluster)
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

    # Calculate cashback percentage
    cashback_percentage = (avg_cashback / avg_order) * 100

    # Round off metrics for better presentation
    avg_order_rounded = round(avg_order, 2)
    avg_cashback_rounded = round(avg_cashback, 2)
    cardholder_count = grouped['cardholder_id'].nunique()

    return avg_order_rounded, avg_cashback_rounded, cardholder_count
    