import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import insights module
try:
    from insights import get_key_metrics, get_sales_trends, get_category_analysis, get_shipping_analysis
except ImportError:
    # Fallback functions if insights module is not available
    def get_key_metrics(df): return {}
    def get_sales_trends(df): return {}
    def get_category_analysis(df): return {}
    def get_shipping_analysis(df): return {}

# Page configuration
st.set_page_config(
    page_title="Amazon Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark gradient theme
   import streamlit as st

st.markdown("""
    <style>
    /* Global white text */
    html, body, [class*="css"] {
        color: white !important;
        background-color: #1e1e1e !important;
    }

    /* Set background for main container */
    .main {
        background-color: #1e1e1e !important;
    }

    /* White text for titles, headers, subheaders */
    .st-bb, .st-cs, .st-bz, .st-co, .st-ct {
        color: white !important;
    }

    /* White text in metric values */
    div[data-testid="stMetric"] {
        color: white !important;
    }

    /* Inputs and labels */
    label, .stTextInput, .stSelectbox, .stSlider, .stRadio, .stCheckbox, .stDateInput {
        color: white !important;
    }

    /* White text in dataframes and tables */
    .stDataFrame, .stTable {
        color: white !important;
    }

    /* White for expander and sidebar titles */
    .streamlit-expanderHeader, .css-1v0mbdj, .css-1d391kg {
        color: white !important;
    }

    /* Override charts */
    svg {
        color: white !important;
    }

    /* Fix Streamlit widgets specifically */
    .css-ffhzg2, .css-1offfwp, .css-1v0mbdj, .css-1d391kg, .css-1ht1j8u {
        color: white !important;
    }

    /* Adjust buttons */
    button {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)
.main-header {
        background: linear-gradient(90deg, #1e3a5f, #2d5a87);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d5a87);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3a5f, #0c1426);
    }
    
    .stSelectbox > div > div {
        background-color: #2d5a87;
        color: white;
    }
    
    .stMultiSelect > div > div {
        background-color: #2d5a87;
        color: white;
    }
    
    .stDateInput > div > div {
        background-color: #2d5a87;
        color: white;
    }
    
    h1, h2, h3 {
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #1e3a5f, #2d5a87);
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2d5a87, #4a90b8);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("data/amazon_sale_report.csv")
    df.columns = df.columns.str.strip()
    return df
def main():
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🛒 Amazon Sales Analytics Dashboard")
    st.markdown("**Professional Sales Intelligence & Analytics Platform**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar filters
    st.sidebar.markdown("## 🔍 Filters & Controls")
    
    # Date range filter (if date column exists)
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    
    # Status filter
    if 'Status' in df.columns:
        status_options = ['All'] + list(df['Status'].unique())
        selected_status = st.sidebar.selectbox("📋 Order Status", status_options)
    else:
        selected_status = 'All'
    
    # Sales Channel filter
    if 'Sales Channel' in df.columns:
        channel_options = ['All'] + list(df['Sales Channel'].unique())
        selected_channel = st.sidebar.selectbox("📱 Sales Channel", channel_options)
    else:
        selected_channel = 'All'
    
    # Category filter
    if 'Category' in df.columns:
        category_options = ['All'] + list(df['Category'].unique())
        selected_categories = st.sidebar.multiselect("🏷️ Categories", category_options, default=['All'])
    else:
        selected_categories = ['All']
    
    # Ship State filter
    if 'ship-state' in df.columns:
        state_options = ['All'] + list(df['ship-state'].unique())
        selected_states = st.sidebar.multiselect("🗺️ Ship States", state_options, default=['All'])
    else:
        selected_states = ['All']
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_status != 'All' and 'Status' in df.columns:
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    
    if selected_channel != 'All' and 'Sales Channel' in df.columns:
        filtered_df = filtered_df[filtered_df['Sales Channel'] == selected_channel]
    
    if 'All' not in selected_categories and 'Category' in df.columns:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
    
    if 'All' not in selected_states and 'ship-state' in df.columns:
        filtered_df = filtered_df[filtered_df['ship-state'].isin(selected_states)]
    
    # Key Metrics Row
    st.markdown("## 📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_orders = len(filtered_df)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🛍️ Total Orders", f"{total_orders:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if 'Amount' in filtered_df.columns:
            total_revenue = filtered_df['Amount'].sum()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("💰 Total Revenue", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if 'Amount' in filtered_df.columns and len(filtered_df) > 0:
            avg_order_value = filtered_df['Amount'].mean()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📈 Avg Order Value", f"${avg_order_value:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📈 Avg Order Value", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        if 'Category' in filtered_df.columns:
            unique_categories = filtered_df['Category'].nunique()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🏷️ Product Categories", f"{unique_categories}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🏷️ Product Categories", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Sales Overview", "🏷️ Category Analysis", "🚚 Shipping Analysis", "🗺️ Geographic Analysis", "📋 Data Explorer"])
    
    with tab1:
        st.markdown("### 📊 Sales Performance Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sales by Status
            if 'Status' in filtered_df.columns:
                status_counts = filtered_df['Status'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Orders by Status",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    template="plotly_dark"
                )
                fig_status.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Sales by Channel
            if 'Sales Channel' in filtered_df.columns:
                channel_counts = filtered_df['Sales Channel'].value_counts()
                fig_channel = px.bar(
                    x=channel_counts.index,
                    y=channel_counts.values,
                    title="Orders by Sales Channel",
                    color=channel_counts.values,
                    color_continuous_scale="Blues",
                    template="plotly_dark"
                )
                fig_channel.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis=dict(title="Sales Channel"),
                    yaxis=dict(title="Number of Orders")
                )
                st.plotly_chart(fig_channel, use_container_width=True)
        
        # Revenue analysis if Amount column exists
        if 'Amount' in filtered_df.columns:
            st.markdown("### 💰 Revenue Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Revenue by Category
                if 'Category' in filtered_df.columns:
                    category_revenue = filtered_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
                    fig_cat_rev = px.bar(
                        x=category_revenue.index,
                        y=category_revenue.values,
                        title="Revenue by Category",
                        color=category_revenue.values,
                        color_continuous_scale="Viridis",
                        template="plotly_dark"
                    )
                    fig_cat_rev.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(title="Category"),
                        yaxis=dict(title="Revenue ($)")
                    )
                    st.plotly_chart(fig_cat_rev, use_container_width=True)
            
            with col2:
                # Revenue by State
                if 'ship-state' in filtered_df.columns:
                    state_revenue = filtered_df.groupby('ship-state')['Amount'].sum().sort_values(ascending=False).head(10)
                    fig_state_rev = px.bar(
                        x=state_revenue.values,
                        y=state_revenue.index,
                        orientation='h',
                        title="Top 10 States by Revenue",
                        color=state_revenue.values,
                        color_continuous_scale="Plasma",
                        template="plotly_dark"
                    )
                    fig_state_rev.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(title="Revenue ($)"),
                        yaxis=dict(title="State")
                    )
                    st.plotly_chart(fig_state_rev, use_container_width=True)
    
    with tab2:
        st.markdown("### 🏷️ Category Performance Analysis")
        
        if 'Category' in filtered_df.columns:
            category_analysis = get_category_analysis(filtered_df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top categories by quantity
                if 'Qty' in filtered_df.columns:
                    cat_qty = filtered_df.groupby('Category')['Qty'].sum().sort_values(ascending=False).head(10)
                    fig_cat_qty = px.treemap(
                        names=cat_qty.index,
                        values=cat_qty.values,
                        title="Product Categories by Quantity Sold",
                        color=cat_qty.values,
                        color_continuous_scale="RdYlBu",
                        template="plotly_dark"
                    )
                    fig_cat_qty.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig_cat_qty, use_container_width=True)
            
            with col2:
                # Category distribution
                cat_dist = filtered_df['Category'].value_counts().head(10)
                fig_cat_dist = px.pie(
                    values=cat_dist.values,
                    names=cat_dist.index,
                    title="Top 10 Categories by Order Count",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    template="plotly_dark"
                )
                fig_cat_dist.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_cat_dist, use_container_width=True)
    
    with tab3:
        st.markdown("### 🚚 Shipping & Fulfillment Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Fulfillment analysis
            if 'Fulfilment' in filtered_df.columns:
                fulfillment_counts = filtered_df['Fulfilment'].value_counts()
                fig_fulfillment = px.pie(
                    values=fulfillment_counts.values,
                    names=fulfillment_counts.index,
                    title="Orders by Fulfillment Type",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    template="plotly_dark"
                )
                fig_fulfillment.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_fulfillment, use_container_width=True)
        
        with col2:
            # Courier analysis
            if 'Courier Status' in filtered_df.columns:
                courier_counts = filtered_df['Courier Status'].value_counts()
                fig_courier = px.bar(
                    x=courier_counts.index,
                    y=courier_counts.values,
                    title="Orders by Courier Status",
                    color=courier_counts.values,
                    color_continuous_scale="Oranges",
                    template="plotly_dark"
                )
                fig_courier.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis=dict(title="Courier Status"),
                    yaxis=dict(title="Number of Orders")
                )
                st.plotly_chart(fig_courier, use_container_width=True)
    
    with tab4:
        st.markdown("### 🗺️ Geographic Sales Distribution")
        
        if 'ship-state' in filtered_df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # State distribution
                state_counts = filtered_df['ship-state'].value_counts().head(15)
                fig_states = px.bar(
                    x=state_counts.values,
                    y=state_counts.index,
                    orientation='h',
                    title="Top 15 States by Order Count",
                    color=state_counts.values,
                    color_continuous_scale="Viridis",
                    template="plotly_dark"
                )
                fig_states.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis=dict(title="Number of Orders"),
                    yaxis=dict(title="State")
                )
                st.plotly_chart(fig_states, use_container_width=True)
            
            with col2:
                # City distribution
                if 'ship-city' in filtered_df.columns:
                    city_counts = filtered_df['ship-city'].value_counts().head(15)
                    fig_cities = px.bar(
                        x=city_counts.values,
                        y=city_counts.index,
                        orientation='h',
                        title="Top 15 Cities by Order Count",
                        color=city_counts.values,
                        color_continuous_scale="Plasma",
                        template="plotly_dark"
                    )
                    fig_cities.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(title="Number of Orders"),
                        yaxis=dict(title="City")
                    )
                    st.plotly_chart(fig_cities, use_container_width=True)
    
    with tab5:
        st.markdown("### 📋 Data Explorer")
        
        # Data summary
        st.markdown("#### 📊 Dataset Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 Total Rows", len(filtered_df))
        with col2:
            st.metric("📊 Total Columns", len(filtered_df.columns))
        with col3:
            st.metric("💾 Memory Usage", f"{filtered_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Column information
        st.markdown("#### 🔍 Column Information")
        col_info = pd.DataFrame({
            'Column': filtered_df.columns,
            'Data Type': filtered_df.dtypes.astype(str),
            'Non-Null Count': filtered_df.count(),
            'Null Count': filtered_df.isnull().sum()
        }).reset_index(drop=True)
        
        st.dataframe(col_info, use_container_width=True)
        
        # Sample data
        st.markdown("#### 📋 Sample Data")
        st.dataframe(filtered_df.head(100), use_container_width=True)
        
        # Download filtered data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name=f'filtered_amazon_sales_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )

if __name__ == "__main__":
    main()
