import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_key_metrics(df):
    """
    Calculate key business metrics from the sales data
    """
    metrics = {}
    
    # Basic metrics
    metrics['total_orders'] = len(df)
    metrics['total_revenue'] = df['Amount'].sum() if 'Amount' in df.columns else 0
    metrics['avg_order_value'] = df['Amount'].mean() if 'Amount' in df.columns else 0
    metrics['total_quantity'] = df['Qty'].sum() if 'Qty' in df.columns else 0
    
    # Advanced metrics
    if 'Amount' in df.columns:
        metrics['revenue_std'] = df['Amount'].std()
        metrics['median_order_value'] = df['Amount'].median()
        metrics['max_order_value'] = df['Amount'].max()
        metrics['min_order_value'] = df['Amount'].min()
    
    # Category metrics
    if 'Category' in df.columns:
        metrics['unique_categories'] = df['Category'].nunique()
        metrics['top_category'] = df['Category'].value_counts().index[0] if len(df) > 0 else 'N/A'
    
    # Geographic metrics
    if 'ship-state' in df.columns:
        metrics['unique_states'] = df['ship-state'].nunique()
        metrics['top_state'] = df['ship-state'].value_counts().index[0] if len(df) > 0 else 'N/A'
    
    if 'ship-city' in df.columns:
        metrics['unique_cities'] = df['ship-city'].nunique()
        metrics['top_city'] = df['ship-city'].value_counts().index[0] if len(df) > 0 else 'N/A'
    
    # Status metrics
    if 'Status' in df.columns:
        status_counts = df['Status'].value_counts()
        metrics['status_distribution'] = status_counts.to_dict()
        metrics['shipped_percentage'] = (status_counts.get('Shipped', 0) / len(df)) * 100 if len(df) > 0 else 0
    
    # Fulfillment metrics
    if 'Fulfilment' in df.columns:
        fulfillment_counts = df['Fulfilment'].value_counts()
        metrics['fulfillment_distribution'] = fulfillment_counts.to_dict()
    
    return metrics

def get_sales_trends(df):
    """
    Analyze sales trends over time
    """
    trends = {}
    
    # Look for date columns
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    
    if date_columns:
        # Use the first date column found
        date_col = date_columns[0]
        try:
            df[date_col] = pd.to_datetime(df[date_col])
            df_sorted = df.sort_values(date_col)
            
            # Daily trends
            daily_sales = df_sorted.groupby(df_sorted[date_col].dt.date).agg({
                'Amount': 'sum' if 'Amount' in df.columns else 'count',
                'Qty': 'sum' if 'Qty' in df.columns else 'count'
            }).reset_index()
            
            trends['daily_sales'] = daily_sales
            
            # Monthly trends
            monthly_sales = df_sorted.groupby(df_sorted[date_col].dt.to_period('M')).agg({
                'Amount': 'sum' if 'Amount' in df.columns else 'count',
                'Qty': 'sum' if 'Qty' in df.columns else 'count'
            }).reset_index()
            
            trends['monthly_sales'] = monthly_sales
            
            # Growth rate calculation
            if len(daily_sales) > 1:
                trends['growth_rate'] = ((daily_sales['Amount'].iloc[-1] - daily_sales['Amount'].iloc[0]) / 
                                       daily_sales['Amount'].iloc[0]) * 100
            
        except Exception as e:
            print(f"Error processing date column: {e}")
            trends['error'] = str(e)
    
    return trends

def get_category_analysis(df):
    """
    Perform detailed category analysis
    """
    analysis = {}
    
    if 'Category' in df.columns:
        # Basic category stats
        category_counts = df['Category'].value_counts()
        analysis['category_counts'] = category_counts.to_dict()
        analysis['top_categories'] = category_counts.head(10).to_dict()
        
        # Revenue by category
        if 'Amount' in df.columns:
            category_revenue = df.groupby('Category')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            category_revenue.columns = ['Category', 'Total_Revenue', 'Avg_Revenue', 'Order_Count']
            category_revenue = category_revenue.sort_values('Total_Revenue', ascending=False)
            analysis['category_revenue'] = category_revenue
        
        # Quantity by category
        if 'Qty' in df.columns:
            category_qty = df.groupby('Category')['Qty'].agg(['sum', 'mean']).reset_index()
            category_qty.columns = ['Category', 'Total_Qty', 'Avg_Qty']
            analysis['category_quantity'] = category_qty
        
        # Category performance metrics
        if 'Amount' in df.columns and 'Qty' in df.columns:
            category_performance = df.groupby('Category').agg({
                'Amount': ['sum', 'mean', 'std'],
                'Qty': ['sum', 'mean'],
                'Order ID': 'count'
            }).reset_index()
            
            category_performance.columns = ['Category', 'Total_Revenue', 'Avg_Revenue', 'Revenue_Std', 
                                          'Total_Qty', 'Avg_Qty', 'Order_Count']
            category_performance['Revenue_per_Unit'] = category_performance['Total_Revenue'] / category_performance['Total_Qty']
            
            analysis['category_performance'] = category_performance
    
    return analysis

def get_shipping_analysis(df):
    """
    Analyze shipping and fulfillment patterns
    """
    analysis = {}
    
    # Fulfillment analysis
    if 'Fulfilment' in df.columns:
        fulfillment_counts = df['Fulfilment'].value_counts()
        analysis['fulfillment_distribution'] = fulfillment_counts.to_dict()
        
        # Revenue by fulfillment type
        if 'Amount' in df.columns:
            fulfillment_revenue = df.groupby('Fulfilment')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            fulfillment_revenue.columns = ['Fulfilment', 'Total_Revenue', 'Avg_Revenue', 'Order_Count']
            analysis['fulfillment_revenue'] = fulfillment_revenue
    
    # Courier analysis
    if 'Courier Status' in df.columns:
        courier_counts = df['Courier Status'].value_counts()
        analysis['courier_distribution'] = courier_counts.to_dict()
    
    # Service level analysis
    if 'ship-service-level' in df.columns:
        service_counts = df['ship-service-level'].value_counts()
        analysis['service_level_distribution'] = service_counts.to_dict()
        
        # Revenue by service level
        if 'Amount' in df.columns:
            service_revenue = df.groupby('ship-service-level')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            service_revenue.columns = ['Service_Level', 'Total_Revenue', 'Avg_Revenue', 'Order_Count']
            analysis['service_level_revenue'] = service_revenue
    
    # Geographic shipping patterns
    if 'ship-state' in df.columns:
        state_counts = df['ship-state'].value_counts()
        analysis['state_distribution'] = state_counts.to_dict()
        analysis['top_states'] = state_counts.head(10).to_dict()
        
        # Revenue by state
        if 'Amount' in df.columns:
            state_revenue = df.groupby('ship-state')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            state_revenue.columns = ['State', 'Total_Revenue', 'Avg_Revenue', 'Order_Count']
            state_revenue = state_revenue.sort_values('Total_Revenue', ascending=False)
            analysis['state_revenue'] = state_revenue
    
    if 'ship-city' in df.columns:
        city_counts = df['ship-city'].value_counts()
        analysis['city_distribution'] = city_counts.to_dict()
        analysis['top_cities'] = city_counts.head(10).to_dict()
    
    return analysis

def get_product_analysis(df):
    """
    Analyze product performance
    """
    analysis = {}
    
    # SKU analysis
    if 'SKU' in df.columns:
        sku_counts = df['SKU'].value_counts()
        analysis['sku_distribution'] = sku_counts.to_dict()
        analysis['top_skus'] = sku_counts.head(10).to_dict()
        
        # Revenue by SKU
        if 'Amount' in df.columns:
            sku_revenue = df.groupby('SKU')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            sku_revenue.columns = ['SKU', 'Total_Revenue', 'Avg_Revenue', 'Order_Count']
            sku_revenue = sku_revenue.sort_values('Total_Revenue', ascending=False)
            analysis['sku_revenue'] = sku_revenue.head(20)  # Top 20 SKUs
    
    # ASIN analysis
    if 'ASIN' in df.columns:
        asin_counts = df['ASIN'].value_counts()
        analysis['asin_distribution'] = asin_counts.to_dict()
        analysis['top_asins'] = asin_counts.head(10).to_dict()
        
        # Revenue by ASIN
        if 'Amount' in df.columns:
            asin_revenue = df.groupby('ASIN')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            asin_revenue.columns = ['ASIN', 'Total_Revenue', 'Avg_Revenue', 'Order_Count']
            asin_revenue = asin_revenue.sort_values('Total_Revenue', ascending=False)
            analysis['asin_revenue'] = asin_revenue.head(20)  # Top 20 ASINs
    
    # Style analysis
    if 'Style' in df.columns:
        style_counts = df['Style'].value_counts()
        analysis['style_distribution'] = style_counts.to_dict()
        analysis['top_styles'] = style_counts.head(10).to_dict()
    
    # Size analysis
    if 'Size' in df.columns:
        size_counts = df['Size'].value_counts()
        analysis['size_distribution'] = size_counts.to_dict()
        analysis['top_sizes'] = size_counts.head(10).to_dict()
        
        # Revenue by size
        if 'Amount' in df.columns:
            size_revenue = df.groupby('Size')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            size_revenue.columns = ['Size', 'Total_Revenue', 'Avg_Revenue', 'Order_Count']
            size_revenue = size_revenue.sort_values('Total_Revenue', ascending=False)
            analysis['size_revenue'] = size_revenue
    
    return analysis

def get_revenue_analysis(df):
    """
    Detailed revenue analysis
    """
    analysis = {}
    
    if 'Amount' in df.columns:
        # Basic revenue statistics
        analysis['total_revenue'] = df['Amount'].sum()
        analysis['avg_revenue'] = df['Amount'].mean()
        analysis['median_revenue'] = df['Amount'].median()
        analysis['revenue_std'] = df['Amount'].std()
        analysis['max_revenue'] = df['Amount'].max()
        analysis['min_revenue'] = df['Amount'].min()
        
        # Revenue distribution
        analysis['revenue_quartiles'] = df['Amount'].quantile([0.25, 0.5, 0.75]).to_dict()
        
        # Revenue segments
        analysis['high_value_orders'] = len(df[df['Amount'] > df['Amount'].quantile(0.9)])
        analysis['medium_value_orders'] = len(df[(df['Amount'] >= df['Amount'].quantile(0.5)) & 
                                               (df['Amount'] <= df['Amount'].quantile(0.9))])
        analysis['low_value_orders'] = len(df[df['Amount'] < df['Amount'].quantile(0.5)])
        
        # Revenue by currency
        if 'currency' in df.columns:
            currency_revenue = df.groupby('currency')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            currency_revenue.columns = ['Currency', 'Total_Revenue', 'Avg_Revenue', 'Order_Count']
            analysis['currency_revenue'] = currency_revenue
    
    return analysis

def get_customer_insights(df):
    """
    Generate customer-related insights
    """
    insights = {}
    
    # Geographic customer distribution
    if 'ship-state' in df.columns:
        state_customers = df['ship-state'].value_counts()
        insights['customers_by_state'] = state_customers.to_dict()
        
        # Customer concentration
        total_orders = len(df)
        top_5_states = state_customers.head(5).sum()
        insights['top_5_states_concentration'] = (top_5_states / total_orders) * 100
    
    if 'ship-city' in df.columns:
        city_customers = df['ship-city'].value_counts()
        insights['customers_by_city'] = city_customers.to_dict()
        
        # Customer concentration by city
        top_10_cities = city_customers.head(10).sum()
        insights['top_10_cities_concentration'] = (top_10_cities / total_orders) * 100
    
    # Postal code analysis
    if 'ship-postal-code' in df.columns:
        postal_customers = df['ship-postal-code'].value_counts()
        insights['customers_by_postal'] = postal_customers.head(20).to_dict()
    
    # Country analysis
    if 'ship-country' in df.columns:
        country_customers = df['ship-country'].value_counts()
        insights['customers_by_country'] = country_customers.to_dict()
    
    return insights

def get_advanced_analytics(df):
    """
    Advanced analytics and business insights
    """
    analytics = {}
    
    # Order size analysis
    if 'Qty' in df.columns:
        analytics['avg_order_size'] = df['Qty'].mean()
        analytics['order_size_distribution'] = df['Qty'].value_counts().to_dict()
        
        # Bulk orders (orders with quantity > 1)
        bulk_orders = df[df['Qty'] > 1]
        analytics['bulk_orders_count'] = len(bulk_orders)
        analytics['bulk_orders_percentage'] = (len(bulk_orders) / len(df)) * 100
    
    # Status analysis
    if 'Status' in df.columns:
        status_dist = df['Status'].value_counts()
        analytics['status_distribution'] = status_dist.to_dict()
        
        # Calculate fulfillment rate
        if 'Shipped' in status_dist.index:
            analytics['fulfillment_rate'] = (status_dist['Shipped'] / len(df)) * 100
    
    # Sales channel effectiveness
    if 'Sales Channel' in df.columns:
        channel_performance = df.groupby('Sales Channel').agg({
            'Amount': ['sum', 'mean', 'count'] if 'Amount' in df.columns else ['count'],
            'Qty': ['sum', 'mean'] if 'Qty' in df.columns else ['count']
        }).reset_index()
        
        if 'Amount' in df.columns:
            channel_performance.columns = ['Sales_Channel', 'Total_Revenue', 'Avg_Revenue', 'Order_Count', 'Total_Qty', 'Avg_Qty']
        else:
            channel_performance.columns = ['Sales_Channel', 'Order_Count', 'Total_Qty']
        
        analytics['channel_performance'] = channel_performance
    
    # Product diversity
    if 'Category' in df.columns:
        analytics['product_diversity'] = df['Category'].nunique()
        
        # Category concentration
        category_counts = df['Category'].value_counts()
        top_3_categories = category_counts.head(3).sum()
        analytics['top_3_categories_concentration'] = (top_3_categories / len(df)) * 100
    
    # Size preferences
    if 'Size' in df.columns:
        size_preferences = df['Size'].value_counts()
        analytics['size_preferences'] = size_preferences.to_dict()
        analytics['most_popular_size'] = size_preferences.index[0] if len(size_preferences) > 0 else 'N/A'
    
    return analytics

def generate_summary_report(df):
    """
    Generate a comprehensive summary report
    """
    report = {}
    
    # Basic summary
    report['dataset_info'] = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'date_range': 'N/A',  # Will be updated if date column exists
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    
    # Business metrics
    report['business_metrics'] = get_key_metrics(df)
    
    # Top performers
    report['top_performers'] = {}
    
    if 'Category' in df.columns:
        report['top_performers']['categories'] = df['Category'].value_counts().head(5).to_dict()
    
    if 'ship-state' in df.columns:
        report['top_performers']['states'] = df['ship-state'].value_counts().head(5).to_dict()
    
    if 'SKU' in df.columns:
        report['top_performers']['skus'] = df['SKU'].value_counts().head(5).to_dict()
    
    # Revenue insights
    if 'Amount' in df.columns:
        report['revenue_insights'] = get_revenue_analysis(df)
    
    # Operational insights
    report['operational_insights'] = {}
    
    if 'Fulfilment' in df.columns:
        report['operational_insights']['fulfillment'] = df['Fulfilment'].value_counts().to_dict()
    
    if 'Courier Status' in df.columns:
        report['operational_insights']['courier_status'] = df['Courier Status'].value_counts().to_dict()
    
    if 'Status' in df.columns:
        report['operational_insights']['order_status'] = df['Status'].value_counts().to_dict()
    
    return report

def create_executive_summary(df):
    """
    Create an executive summary for stakeholders
    """
    summary = {}
    
    # Key highlights
    summary['key_highlights'] = []
    
    # Total business volume
    total_orders = len(df)
    summary['key_highlights'].append(f"Processed {total_orders:,} orders")
    
    if 'Amount' in df.columns:
        total_revenue = df['Amount'].sum()
        avg_order_value = df['Amount'].mean()
        summary['key_highlights'].append(f"Generated ${total_revenue:,.2f} in total revenue")
        summary['key_highlights'].append(f"Average order value: ${avg_order_value:.2f}")
    
    # Geographic reach
    if 'ship-state' in df.columns:
        unique_states = df['ship-state'].nunique()
        summary['key_highlights'].append(f"Served customers in {unique_states} states")
    
    if 'ship-city' in df.columns:
        unique_cities = df['ship-city'].nunique()
        summary['key_highlights'].append(f"Delivered to {unique_cities} cities")
    
    # Product diversity
    if 'Category' in df.columns:
        unique_categories = df['Category'].nunique()
        summary['key_highlights'].append(f"Sold products across {unique_categories} categories")
    
    # Operational performance
    if 'Status' in df.columns:
        status_counts = df['Status'].value_counts()
        if 'Shipped' in status_counts.index:
            shipped_rate = (status_counts['Shipped'] / total_orders) * 100
            summary['key_highlights'].append(f"Achieved {shipped_rate:.1f}% shipping rate")
    
    # Growth opportunities
    summary['growth_opportunities'] = []
    
    if 'Category' in df.columns and 'Amount' in df.columns:
        category_revenue = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        top_category = category_revenue.index[0]
        summary['growth_opportunities'].append(f"Focus on expanding {top_category} category")
    
    if 'ship-state' in df.columns:
        state_counts = df['ship-state'].value_counts()
        underserved_states = state_counts[state_counts < state_counts.quantile(0.25)]
        if len(underserved_states) > 0:
            summary['growth_opportunities'].append(f"Opportunity to expand in {len(underserved_states)} underserved states")
    
    return summary
