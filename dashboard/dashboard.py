import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import FastMarkerCluster, HeatMap, Fullscreen

sns.set(style='dark')

def plot_review_scores(df):
    # Calculate the average review score for each product category
    average_review_scores = df.groupby('product_category_name_english')['review_score'].mean()

    # Sort the scores for better visualization
    average_review_scores = average_review_scores.sort_values()

    # Get top 10 categories with highest and lowest average review scores
    top_10 = average_review_scores.tail(10)
    bottom_10 = average_review_scores.head(10)

    # Create subplots
    fig, axs = plt.subplots(1, 2, figsize=(15, 10))

    # Plot top 10 categories
    sns.barplot(x=top_10.values[::-1], y=top_10.index[::-1], ax=axs[0], palette="Blues_d")
    axs[0].set_title('Top 10 Categories with Highest Average Review Scores')
    axs[0].set_xlabel('Average Review Score')
    axs[0].set_ylabel('')

    # Plot bottom 10 categories
    sns.barplot(x=bottom_10.values[::-1], y=bottom_10.index[::-1], ax=axs[1], palette="Blues_d")
    axs[1].set_title('Top 10 Categories with Lowest Average Review Scores')
    axs[1].set_xlabel('Average Review Score')
    axs[1].set_ylabel('')

    # Display the plots
    plt.tight_layout()
    return fig

def plot_product_trends(df):
    # Sales trends for products
    sales_by_category = df.groupby('product_category_name_english')['order_item_id'].sum().sort_values(ascending=False).head(10)

    # Create a figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Use Seaborn for the bar plot
    sns.barplot(y=sales_by_category.index, x=sales_by_category.values, palette="crest", orient='h', ax=ax)
    ax.set_title('Sales Trends by Product Category')
    ax.set_ylabel('')
    ax.set_xlabel('')

    return fig

def plot_customer_map(df):
    # Assign the maximum and minimum longitude for the map
    max_lon, min_lon = -30.943182612367426, -75

    # Assign the maximum and minimum latitude for the map
    max_lat, min_lat = 6.104935381074177, -33.71758386653152

    # Create a list of tuples, where each tuple contains the latitude and longitude of a customer
    customer_loc = list(zip(df['customer_lat'], df['customer_lng']))

    # Create a folium map object, centered at latitude -15 and longitude -50, with a zoom level of 3.5
    map_customer = folium.Map(location=[-15, -50], 
                              zoom_start=3.5,     
                              min_lat=min_lat,
                              max_lat=max_lat,
                              min_lon=min_lon,
                              max_lon=max_lon,
                              max_bounds=True,
                              tiles="Cartodb dark_matter")

    # Add a FastMarkerCluster to the map, which will group close markers together for better visualization
    FastMarkerCluster(data=customer_loc).add_to(map_customer)
    
    # Add a Fulscreen view to the map
    folium.plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(map_customer)


    # Return the map
    return map_customer

def plot_heatmap(df):
    # Assign the maximum and minimum longitude for the map
    max_lon, min_lon = -30.943182612367426, -75

    # Assign the maximum and minimum latitude for the map
    max_lat, min_lat = 6.104935381074177, -33.71758386653152

    # Group by latitude and longitude and count the number of orders for each location
    heat_customer_data = df.groupby(['customer_lat','customer_lng'],as_index=False).count().iloc[:, :3]

    # Create a folium map object
    heatmap_customer = folium.Map(
        location=[-15, -50], 
        zoom_start=4.5, 
        tiles='cartodbdark_matter',
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        max_bounds=True
    )

    # Add a HeatMap to the map
    HeatMap(
        name='Mapa de Calor',
        data=heat_customer_data,
        radius=10,
        max_zoom=15
    ).add_to(heatmap_customer)
    
    # Add a Fulscreen view to the map
    folium.plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(heatmap_customer)

    # Return the map
    return heatmap_customer


# Load dataset and cleaning
all_df = pd.read_csv(os.path.join(os.getcwd(),"dashboard/all_df.csv"))
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)
all_df['order_approved_at'] = pd.to_datetime(all_df['order_approved_at'])

# Assign date filter in sidebar menu
min_date = all_df['order_approved_at'].min()
max_date = all_df['order_approved_at'].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Time',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]

st.header('Analysis E-Commerce')

# Dynamic metrics display
col1, col2 = st.columns(2)

with col1:
    total_sales = main_df['payment_value'].sum()
    st.metric("Total Sales", value=f"R$ {round(total_sales):,}")

with col2:
    total_orders = main_df['order_item_id'].sum()
    st.metric("Total Orders", value=f"{round(total_orders):,} Orders")

# Visualization for Top Products
st.subheader('Top Products')

fig_review_score = plot_review_scores(main_df)
st.pyplot(fig_review_score)

fig_top_product = plot_product_trends(main_df)
st.pyplot(fig_top_product)



# Additional Visualization
st.subheader('Distributed Customer')


map_customer = plot_customer_map(main_df)
folium_static(map_customer)


heatmap_customer = plot_heatmap(main_df)
folium_static(heatmap_customer)


st.subheader("Conclusion")
st.write("""
Based on my analysis, here are the key takeaways:

1. The majority of products purchased by customers weigh less than 1 kilogram. This could indicate a preference for lightweight items or digital goods.
2. In terms of review scores, the top three categories are flowers, children’s fashion clothes, and male fashion clothing. These categories consistently receive high ratings from customers. On the other hand, home comfort (2nd category), furniture/mattresses/upholstery, and fashion sport are the three categories with the lowest average review scores.
3. The most popular product categories among Brazilian customers are bed/bath/table, furniture/decor, and health/beauty. These categories may represent essential and frequently used items in daily life.
4. Customers are widely distributed across more than half of Brazil, with a significant concentration near Sao Paulo. This city alone ordered for nearly 90,000 customers between 2017 and 2018.
5. August is the peak month for purchases, which could be related to specific events, holidays, or seasonal shopping habits.
Weekdays are the most popular days for making purchases. This could be due to the availability of customers or specific shopping habits during the workweek.
6. Afternoon is the most popular time of day for customers to make purchases. This could be when customers have free time or when they are most likely to engage in online shopping.
7. The majority of customers prefer to use credit cards for their purchases. This could indicate a preference for the convenience and security offered by credit card transactions.

In conclusion, businesses could focus on improving the quality of products in categories with lower review scores or consider offering promotions during peak shopping times.

""")