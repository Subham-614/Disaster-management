import base64
import streamlit as st
import numpy as np
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import plotly.express as px
from ipyleaflet import Map, Marker, CircleMarker
from streamlit.components.v1 import html
import pydeck as pdk
import requests
from pymongo import MongoClient
import schedule
import time
import threading
import base64

# MongoDB Atlas connection string (replace <username>, <password>, <cluster> with your own credentials)
MONGO_URI = 'mongodb+srv://surya:mongo1234@cluster0.686u6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGO_URI)

# Select the database and collection in MongoDB
db = client['news_db']  # Database name
collection = db['google_news_articles']  # Collection name

# SerpApi parameters
API_KEY = '4f2e701f069c18eb50de29437aab7f3cd83eda48f88c017f2845d692df40d120'  # Replace with your actual SerpApi key
params = {
    'q': 'flood',  # Search query (e.g., disaster-related news)
    'tbm': 'nws',  # Google News search
    'api_key': API_KEY
}

url = 'https://serpapi.com/search.json'
    
st.set_page_config(page_title="Disaster Management", page_icon="🌀")

# Set background image using custom CSS
def set_bg_image(image_file):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{image_file}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Load your background image
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        import base64
        return base64.b64encode(img_file.read()).decode()

# Replace 'background.jpg' with your image file path
bg_image_base64 = get_base64_image("new_bg.jpg")
set_bg_image(bg_image_base64)



# Sidebar for page selection
page = st.sidebar.radio("Select Page", ["Home", "Floods", "Landslide", "Earthquake", "Helpline", "Contact Us"])

# --------------------------------------
# Function: Home Page
def home_page():
    st.header("Welcome to the Disaster Management Dashboard")
    st.write("""
        This platform provides real-time updates and resources for managing disaster-related situations.
        Stay informed and prepared.
    """)
    st.info("""
    Heavy rainfall and flooding from the Southwest Monsoon have caused widespread 
damage and casualties in western and southeastern India since late August. As 
of September 2, 2024, the National Emergency Response Centre (NDMI) reported 
61 fatalities, 42 injured people, 38,377 evacuated people, and more than 8 
million people affected in Gujarat.

Landslides in Wayanad, Kerala have highlighted the need for sustainable 
development. Survivors are pinning their hopes on government help, 
and some areas may be out of bounds forever.

GUWAHATI, India, June 14 (Reuters) - At least six people have been killed 
this week and around 2,000 tourists stranded in India's Himalayan state of 
Sikkim in landslides and floods after incessant rainfall, 
officials said on Friday.
Another four people have been killed in Nepal's Taplejung district, 
which borders Sikkim, after a landslide following rains swept away the house 
in which they were sleeping, officials there said.
Heavy rains triggered landslides at several locations in Mangan district, 
which covers north Sikkim and lies about 100 km (60 miles) north of the state 
capital Gangtok, the local government of the northeastern Indian state said.
    """)
    st.info("""
    IMPORTANT LINKS :- 
    1. [Wayanad Landslide](https://www.ndtv.com/india-news/wayanad-landslides-kerala-high-court-wants-holistic-approach-in-development-6302017)
    2. [Gujurat Flood Crisis](https://www.business-standard.com/india-news/gujarat-flooding-worsened-by-extensive-urban-development-shows-study-124090400115_1.html)
    3. [Assam Flood](https://www.downtoearth.org.in/natural-disasters/assam-floods-2024-unprecedented-timing-and-fury-grips-state)
    """)
    def update_database():
        print("Updating the database...")

        # First, delete the old data
        delete_result = collection.delete_many({})
        print(f"Deleted {delete_result.deleted_count} old articles.")

        # Fetch new data from SerpApi
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            news_articles = data.get('news_results', [])  # Get the news results
            
            # Loop through the articles and insert them into MongoDB
            for article in news_articles:
                try:
                    # Prepare the document for MongoDB
                    document = {
                        'title': article['title'],  # Title of the article
                        'link': article['link'],    # Link to the article
                        'source': article.get('source', ''),  # News source (if available)
                        'date': article.get('date', ''),  # Publication date (if available)
                        'snippet': article.get('snippet', ''),  # Snippet/summary of the article
                        'thumbnail': article.get('thumbnail', ''),  # Thumbnail image URL (if available)
                    }
                    
                    # Insert the document into MongoDB
                    result = collection.insert_one(document)
                    print(f"Inserted article with ID: {result.inserted_id}")
                except Exception as e:
                    print(f"An error occurred while inserting data: {e}")
        else:
            print(f"Failed to fetch Google News. Status code: {response.status_code}")

    def run_scheduler():
        # Schedule the job to run at midnight
        schedule.every().day.at("00:00").do(update_database)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    # Run the scheduler in a separate thread
    def start_scheduler():
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()

    # Streamlit app logic
    st.title('Current News Articles')

    # Fetch news articles from MongoDB
    news_articles = collection.find()

    # Organize the display in rows with 2 articles per row
    cols = st.columns(1)
    col_idx = 0

    for article in news_articles:
        with cols[col_idx]:
            # Display the thumbnail (if available) and the article details
            if article.get('thumbnail'):
                st.image(article['thumbnail'], width=200)
            st.write(f"**Title**: {article['title']}")
            st.write(f"**Source**: {article.get('source', 'Unknown')}")
            st.write(f"**Date**: {article.get('date', 'Unknown')}")
            st.write(f"**Snippet**: {article.get('snippet', 'No summary available')}")
            st.write(f"[Read more]({article['link']})")
        
        # Alternate between the two columns
        col_idx = (col_idx + 1) % 1

    # Start the scheduler when the Streamlit app runs
    start_scheduler()
    
    # Example visualizations for the Home page
    df = pd.read_csv('Disaster.csv')
    
    # Line chart: Total deaths over the years
    fig = px.line(df, x='Year', y='Total Deaths', title='Total Deaths Over Time')
    st.plotly_chart(fig)

    # Bar chart: Total deaths by Disaster Type
    fig = px.bar(df, x='Disaster Type', y='Total Deaths', title='Total Deaths by Disaster Type')
    st.plotly_chart(fig)
    
    # Pie chart: Total deaths by Continent
    fig = px.pie(df, values='Total Deaths', names='Continent', title='Total Deaths by Continent')
    st.plotly_chart(fig)
    st.markdown("# Total people affected by disasters")
    def convert_to_numeric(coord):
        try:
            return float(coord)
        except ValueError:
            return np.nan
    df['Latitude'] = df['Latitude'].apply(convert_to_numeric)
    df['Longitude'] = df['Longitude'].apply(convert_to_numeric)
    geo_df = df.dropna(subset=['Latitude', 'Longitude', 'Total Deaths'])

    # Create a base map
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers
    for i, row in geo_df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=(
                f"<strong>Event Name:</strong> {row['Event Name']}<br>"
                f"<strong>Country:</strong> {row['Country']}<br>"
                f"<strong>Year:</strong> {row['Year']}<br>"
                f"<strong>Total Deaths:</strong> {row['Total Deaths']}<br>"
                f"<strong>Disaster Type:</strong> {row['Disaster Type']}"
            ),
            icon=folium.Icon(color="red" if row['Total Deaths'] > 100 else "blue", icon="info-sign")
        ).add_to(marker_cluster)

    # Display the map
    folium_static(m)

# --------------------------------------
# Function: Floods Page
def floods_page():
    df = pd.read_csv('Flood_data_clean.csv')
    st.header("Distribution of Flood Duration")
    
    # Histogram of flood duration
    fig = px.histogram(df, x='Duration(Days)', nbins=20, title='Distribution of Flood Duration')
    fig.update_layout(xaxis_title='Duration (Days)', yaxis_title='Count')
    st.plotly_chart(fig)

# Check if relevant columns exist
    st.header("Flood Events by Year")

    # Extract year from Start Date
    df['Year'] = pd.to_datetime(df['Start Date']).dt.year

    # Bar chart of flood events by year
    fig = px.bar(df.groupby('Year').size().reset_index(name='Event Count'),
                x='Year', y='Event Count', title='Flood Events by Year')

    st.plotly_chart(fig)
    st.header("Area Affected vs. Human Displacement")

    st.header("Flood Locations Map")

    # Drop rows with missing latitude or longitude
    df_clean = df.dropna(subset=['Latitude', 'Longitude'])

    # Create a base map
    m = folium.Map(location=[22, 78], zoom_start=5, tiles='OpenStreetMap')

    # Add markers to the map
    for i, row in df_clean.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=(
                f"<strong>Location:</strong> {row['Location']}<br>"
                f"<strong>Districts:</strong> {row['Districts']}<br>"
                f"<strong>Severity:</strong> {row['Severity']}<br>"
                f"<strong>Human Fatality:</strong> {row['Human fatality']}<br>"
                f"<strong>Area Affected:</strong> {row['Area Affected']}"
            ),
            icon=folium.Icon(color="red" if row['Severity'] == 'Severe' else "blue")
        ).add_to(m)

    # Display the map in Streamlit
    folium_static(m)

    # Ensure that 'Start Date' is in datetime format
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')

    # Drop rows where 'Start Date' could not be converted to datetime
    df = df.dropna(subset=['Start Date'])

    # Set 'Start Date' as the index
    df.set_index('Start Date', inplace=True)

    # Time-Series Plot (Event counts over time)
    st.write("### Event Count Over Time")
    df['Event Count'] = 1
    time_series = df.resample('ME').sum()['Event Count']  # Resample monthly

    # Plot the time-series data
    fig4 = px.line(time_series, 
                title="Events Over Time (Monthly Aggregated)",
                labels={'Start Date': 'Time', 'value': 'Event Count'})
    st.plotly_chart(fig4)

    st.header("Heatmap of Human Fatalities")

    # Filter for valid latitude and longitude
    df_heatmap = df.dropna(subset=['Latitude', 'Longitude', 'Human fatality'])

    # Create a base map
    m_heatmap = folium.Map(location=[22, 78], zoom_start=5)

    # Create a heatmap
    heat_data = [[row['Latitude'], row['Longitude'], row['Human fatality']] for index, row in df_heatmap.iterrows()]
    HeatMap(heat_data).add_to(m_heatmap)

    # Display the map in Streamlit
    folium_static(m_heatmap)

    # Pie Chart: Affected Areas by Main Cause
    st.write("### Affected Areas by Event Type")
    cause_area_group = df.groupby('Main Cause')['Area Affected'].sum().reset_index()

    fig9 = px.pie(cause_area_group, 
                names='Main Cause', 
                values='Area Affected', 
                title="Percentage of Affected Areas by Event Type")
    st.plotly_chart(fig9)

# --------------------------------------
# Function: Landslide Page
def landslide_page():
    df = pd.read_csv("Global_Landslide_Catalog_Export.csv")

    st.header("Landslide Category Breakdown")

    # Count the number of landslides in each category
    category_count = df['landslide_category'].value_counts().reset_index()
    category_count.columns = ['Landslide Category', 'Count']  # Rename columns for clarity

    # Create the bar plot
    fig = px.bar(category_count, x='Landslide Category', y='Count', 
                labels={'Landslide Category': 'Landslide Category', 'Count': 'Count'},
                title="Landslide Categories")

    st.plotly_chart(fig)
     # Event Distribution by Date (Time-Series Plot)
    st.write("### Event Distribution Over Time")
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    df = df.dropna(subset=['event_date'])
    df.set_index('event_date', inplace=True)
    event_time_series = df.resample('ME').size()

    fig3 = px.line(event_time_series, 
                   title="Event Distribution Over Time (Monthly Aggregated)",
                   labels={'event_date': 'Time', 'value': 'Event Count'})
    st.plotly_chart(fig3)
     # Landslide Size by Setting
    st.write("### Landslide Size by Setting")
    fig4 = px.box(df, 
                  x='landslide_setting', 
                  y='landslide_size', 
                  title="Landslide Size by Setting", 
                  color='landslide_setting')
    st.plotly_chart(fig4)
     # Event Locations on Map
    st.write("### Event Locations on Map")
    fig5 = px.scatter_geo(df, 
                          lat='latitude', 
                          lon='longitude', 
                          color='country_name', 
                          hover_name='event_title', 
                          title="Event Locations on Map")
    st.plotly_chart(fig5)

    st.header("Landslide Category Distribution")

    # Count the number of occurrences in each landslide category
    category_counts = df['landslide_category'].value_counts().reset_index()
    category_counts.columns = ['Landslide Category', 'Count']  # Rename columns for clarity

    # Create the pie chart
    fig = px.pie(category_counts, 
                names='Landslide Category', 
                values='Count', 
                title='Distribution of Landslide Categories',
                labels={'Landslide Category': 'Category', 'Count': 'Count'},
                hole=0.3)  # Optional: set hole size for a donut chart

    # Display the pie chart in Streamlit
    st.plotly_chart(fig)


# --------------------------------------
# Function: Earthquake Page
def earthquake_page():
    df = pd.read_csv("Indian_earthquake_data.csv")
    # Convert 'Origin Time' to datetime
    df['Origin Time'] = pd.to_datetime(df['Origin Time'])

    # Create a time series plot of earthquake frequency
    fig = px.line(df, x="Origin Time", y="Magnitude", title="Earthquake Magnitude Over Time")

    # Display the plot in Streamlit
    st.plotly_chart(fig)
    # Create a scatter plot
    fig = px.scatter(df, x="Magnitude", y="Depth", color="Location",
                    size="Magnitude", hover_name="Location", 
                    title="Magnitude vs Depth of Earthquakes")

    # Display the plot in Streamlit
    st.plotly_chart(fig)

    magnitude_range = st.slider("Select Magnitude Range", 
                                min_value=float(df['Magnitude'].min()), 
                                max_value=float(df['Magnitude'].max()), 
                                value=(float(df['Magnitude'].min()), float(df['Magnitude'].max())))

    # Filter the dataframe based on the selected magnitude range
    filtered_df = df[(df['Magnitude'] >= magnitude_range[0]) & (df['Magnitude'] <= magnitude_range[1])]

    # Define the layer for earthquake points
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_df,
        get_position='[Longitude, Latitude]',
        get_radius=50000,  # Set point size
        get_fill_color='[255, 0, 0, 140]' if df['Magnitude'].mean() > 5 else '[0, 0, 255, 140]',
        pickable=True,
        auto_highlight=True
    )

    # Set the viewport for the map
    view_state = pdk.ViewState(
        latitude=filtered_df['Latitude'].mean(),
        longitude=filtered_df['Longitude'].mean(),
        zoom=2,
        pitch=0
    )

    # Render the map
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Location}\nMagnitude: {Magnitude}"})
    st.pydeck_chart(r)


    # Create a 3D scatter plot
    fig = px.scatter_3d(df, x="Longitude", y="Latitude", z="Depth", 
                        color="Magnitude", size="Magnitude", 
                        hover_name="Location", title="3D Scatter Plot of Earthquakes")

    # Display the plot in Streamlit
    st.plotly_chart(fig)

    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Create a base map
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=2)

    # Prepare data for heatmap (Latitude, Longitude, Magnitude)
    heat_data = [[row['Latitude'], row['Longitude'], row['Magnitude']] for index, row in df.iterrows()]

    # Add heatmap layer
    HeatMap(heat_data).add_to(m)

    # Display the map in Streamlit
    st_folium(m, width=700, height=500)

# Function: Helpline Page
def helpline_page():
    st.header("Emergency Helplines")
    st.write("""
    In case of emergencies related to natural disasters, please contact the following helplines:
    """)
    st.markdown("""
    - **Red Cross:** 1860-266-2345
    - **Fire Department:** 101
    - **Police Department:** 100
    - **NDRF:** 0671-2879711
    - **NDMA:** 011-1070
    - [Contact NDRF](https://www.ndrf.gov.in/contact-us)
    - [Contact NDMA](https://ndma.gov.in/about-us/Contact-us)
    """)

# Function: Contact Us Page
def contact_us_page():
    st.header("Contact Us")
    st.write("""
    For any inquiries or feedback, please reach out to us at:
    - **Email:** support@disastermanagement.org
    - **Phone:** +91-22-12345678
    - **Address:** Disaster Management Building, 1st Floor, National Emergency Center, New Delhi, India
    """)
    st.write("You can also fill out our [contact form](https://www.disastermanagement.org/contact).")

# --------------------------------------
# Run the page functions based on the sidebar selection
if page == "Home":
    home_page()
elif page == "Floods":
    floods_page()
elif page == "Landslide":
    landslide_page()
elif page == "Earthquake":
    earthquake_page()
elif page == "Helpline":
    helpline_page()
elif page == "Contact Us":
    contact_us_page()