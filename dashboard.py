import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Pizza Sales Dashboard", page_icon="🍕", layout="wide")

# Custom CSS for sidebar (dark theme)
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #1e1e2f;
        padding: 1rem;
    }
    .sidebar-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .filter-label {
        font-weight: 600;
        color: #ffffff;
        margin: 0.5rem 0 0.3rem 0;
        font-size: 0.95rem;
    }
    hr {
        margin: 0.8rem 0;
    }
    .stCheckbox {
        margin-bottom: -0.5rem;
    }
    .stButton button {
        background-color: #3a3a4a;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('pizza_sales_cleaned.csv')
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

df = load_data()

# Date range
min_date = df['order_date'].min().strftime('%d %b %Y')
max_date = df['order_date'].max().strftime('%d %b %Y')

# ========== INITIALIZE SESSION STATE ==========
if 'cat_states' not in st.session_state:
    all_cats = sorted(df['pizza_category'].unique())
    st.session_state.cat_states = {cat: True for cat in all_cats}
if 'size_states' not in st.session_state:
    all_sizes = sorted(df['pizza_size'].unique())
    st.session_state.size_states = {sz: True for sz in all_sizes}
if 'day_states' not in st.session_state:
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    st.session_state.day_states = {day: True for day in days_order}

# Reset function with rerun
def reset_all():
    for cat in st.session_state.cat_states:
        st.session_state.cat_states[cat] = True
    for sz in st.session_state.size_states:
        st.session_state.size_states[sz] = True
    for day in st.session_state.day_states:
        st.session_state.day_states[day] = True
    st.rerun()  # Force immediate rerun to refresh checkboxes

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown('<div class="sidebar-header">🍕 Pizza Dashboard</div>', unsafe_allow_html=True)
    
    # Category checkboxes
    st.markdown('<div class="filter-label">📂 Pizza Category</div>', unsafe_allow_html=True)
    for cat in sorted(st.session_state.cat_states.keys()):
        st.session_state.cat_states[cat] = st.checkbox(
            cat.capitalize(), 
            value=st.session_state.cat_states[cat], 
            key=f"cat_{cat}"
        )
    selected_cats = [cat for cat, checked in st.session_state.cat_states.items() if checked]
    
    st.markdown("---")
    
    # Size checkboxes
    st.markdown('<div class="filter-label">📏 Pizza Size</div>', unsafe_allow_html=True)
    for sz in sorted(st.session_state.size_states.keys()):
        st.session_state.size_states[sz] = st.checkbox(
            sz.upper(), 
            value=st.session_state.size_states[sz], 
            key=f"size_{sz}"
        )
    selected_sizes = [sz for sz, checked in st.session_state.size_states.items() if checked]
    
    st.markdown("---")
    
    # Day checkboxes
    st.markdown('<div class="filter-label">📆 Day of Week</div>', unsafe_allow_html=True)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in days_order:
        st.session_state.day_states[day] = st.checkbox(
            day, 
            value=st.session_state.day_states[day], 
            key=f"day_{day}"
        )
    selected_days = [day for day, checked in st.session_state.day_states.items() if checked]
    
    st.markdown("---")
    
    # Holiday checkbox
    st.markdown('<div class="filter-label">🎉 Holiday Filter</div>', unsafe_allow_html=True)
    show_holiday_only = st.checkbox("Show only holidays", value=False)
    
    st.markdown("---")
    
    # Reset All button (now works)
    if st.button("🔄 Reset All Filters", use_container_width=True):
        reset_all()

# Apply filters
filtered_df = df[
    (df['pizza_category'].isin(selected_cats)) &
    (df['pizza_size'].isin(selected_sizes)) &
    (df['day_name'].isin(selected_days))
]

if show_holiday_only:
    filtered_df = filtered_df[filtered_df['is_holiday'] == True]

if filtered_df.empty:
    st.warning("No data matches the selected filters. Please check at least one option.")
    st.stop()

# ========== MAIN DASHBOARD ==========
# Date as normal subtext above title
st.caption(f"📅 Data period: {min_date} – {max_date}")
st.title("🍕 Pizza Sales Operational Dashboard")
st.markdown("---")

# Key metrics
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

# Hourly revenue
col1, col2 = st.columns(2)
with col1:
    st.subheader("⏰ Revenue by Hour")
    hourly = filtered_df.groupby('hour')['total_price'].sum().reset_index()
    fig1 = px.line(hourly, x='hour', y='total_price', markers=True,
                   labels={'hour': 'Hour (0-23)', 'total_price': 'Revenue ($)'},
                   color_discrete_sequence=['#FF4B4B'])
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📆 Revenue by Day of Week")
    daily = filtered_df.groupby('day_name')['total_price'].sum().reindex(days_order).reset_index()
    daily.columns = ['day_name', 'total_price']
    fig2 = px.bar(daily, x='day_name', y='total_price', color='total_price',
                  color_continuous_scale='Reds', labels={'day_name': '', 'total_price': 'Revenue ($)'})
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Category and size
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏷️ Revenue by Pizza Category")
    cat = filtered_df.groupby('pizza_category')['total_price'].sum().sort_values().reset_index()
    fig3 = px.bar(cat, x='total_price', y='pizza_category', orientation='h',
                  color='total_price', color_continuous_scale='Greens')
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("📏 Revenue by Pizza Size")
    size_data = filtered_df.groupby('pizza_size')['total_price'].sum().reset_index()
    fig4 = px.pie(size_data, values='total_price', names='pizza_size', hole=0.3,
                  color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Holiday effect and top 5
col1, col2 = st.columns(2)
with col1:
    st.subheader("🎉 Holiday vs Non-Holiday Revenue")
    holiday_data = filtered_df.groupby('is_holiday')['total_price'].sum().reset_index()
    holiday_data['is_holiday'] = holiday_data['is_holiday'].map({True: 'Holiday', False: 'Non-Holiday'})
    fig5 = px.pie(holiday_data, values='total_price', names='is_holiday', hole=0.4,
                  color_discrete_map={'Holiday': '#FF4B4B', 'Non-Holiday': '#4B9EFF'})
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("🏆 Top 5 Best-Selling Pizzas")
    top5 = filtered_df.groupby('pizza_name')['total_price'].sum().nlargest(5).reset_index()
    top5.columns = ['Pizza Name', 'Revenue ($)']
    st.dataframe(top5, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Use sidebar checkboxes to filter data. Click 'Reset All Filters' to restore defaults.")
