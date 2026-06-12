import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Pizza Sales Dashboard",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load cleaned data
@st.cache_data
def load_data():
    df = pd.read_csv('pizza_sales_cleaned.csv')
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

df = load_data()

# Sidebar filters
st.sidebar.title("🍕 Filters")
selected_categories = st.sidebar.multiselect(
    "Pizza Category",
    options=sorted(df['pizza_category'].unique()),
    default=sorted(df['pizza_category'].unique())
)

show_holiday_only = st.sidebar.checkbox("📅 Show only holidays", False)

# Apply filters
filtered_df = df[df['pizza_category'].isin(selected_categories)]
if show_holiday_only:
    filtered_df = filtered_df[filtered_df['is_holiday'] == True]

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🍕 Pizza Sales Operational Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# ----- Row 1: Key Metrics -----
col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df['total_price'].sum()
total_quantity = filtered_df['quantity'].sum()
avg_daily_revenue = filtered_df.groupby('order_date')['total_price'].sum().mean()
total_orders = filtered_df['order_id'].nunique()

col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
col2.metric("🍕 Pizzas Sold", f"{total_quantity:,}")
col3.metric("📊 Avg Daily Revenue", f"${avg_daily_revenue:,.2f}")
col4.metric("🧾 Total Orders", f"{total_orders:,}")

st.markdown("---")

# ----- Row 2: Hourly & Daily Trends (side by side) -----
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏰ Revenue by Hour of Day")
    hourly_data = filtered_df.groupby('hour')['total_price'].sum().reset_index()
    fig1 = px.line(hourly_data, x='hour', y='total_price', markers=True,
                   labels={'hour': 'Hour (0-23)', 'total_price': 'Revenue ($)'},
                   color_discrete_sequence=['#FF4B4B'])
    fig1.update_layout(hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📆 Revenue by Day of Week")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_data = filtered_df.groupby('day_name')['total_price'].sum().reindex(day_order).reset_index()
    daily_data.columns = ['day_name', 'total_price']
    fig2 = px.bar(daily_data, x='day_name', y='total_price', 
                  color='total_price', color_continuous_scale='Reds',
                  labels={'day_name': '', 'total_price': 'Revenue ($)'})
    fig2.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ----- Row 3: Category Performance & Holiday Effect -----
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏷️ Revenue by Pizza Category")
    cat_data = filtered_df.groupby('pizza_category')['total_price'].sum().sort_values().reset_index()
    fig3 = px.bar(cat_data, x='total_price', y='pizza_category', orientation='h',
                  color='total_price', color_continuous_scale='Greens',
                  labels={'total_price': 'Revenue ($)', 'pizza_category': ''})
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🎉 Holiday vs Non-Holiday Revenue")
    holiday_data = filtered_df.groupby('is_holiday')['total_price'].sum().reset_index()
    holiday_data['is_holiday'] = holiday_data['is_holiday'].map({True: 'Holiday', False: 'Non-Holiday'})
    fig4 = px.pie(holiday_data, values='total_price', names='is_holiday',
                  color='is_holiday', color_discrete_map={'Holiday': '#FF4B4B', 'Non-Holiday': '#4B9EFF'},
                  hole=0.4)
    fig4.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ----- Row 4: Top 5 Pizzas (Table) -----
st.subheader("🏆 Top 5 Best-Selling Pizzas (by Revenue)")
top_pizzas = filtered_df.groupby('pizza_name')['total_price'].sum().nlargest(5).reset_index()
top_pizzas.columns = ['Pizza Name', 'Revenue ($)']
st.dataframe(top_pizzas, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption("📊 Dashboard updates automatically based on filters. Data covers Jan–Dec 2015.")