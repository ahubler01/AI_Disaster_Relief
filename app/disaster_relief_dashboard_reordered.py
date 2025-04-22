import streamlit as st
import streamlit.components.v1 as components
from final_addons.density_map import create_population_density_map
from final_addons.elevation_with_poi import create_elevation_poi_map
from final_addons.response_time_map import create_response_time_map
from tsunami.sunda_density_map import create_sunda_population_density_map
from tsunami.elevation_with_poi_sunda import create_elevation_poi_map as create_sunda_elevation_map
from tsunami.response_time_map_sunda import create_response_time_map as create_sunda_response_map
import json
import base64

def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

st.set_page_config(
    page_title="Disaster Relief Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Encode background images to base64
main_bg_base64 = get_base64_of_image(
    r"C:/Users/yanit/OneDrive/Bureau/Data Insights And Visualization/wallpaperflare.com_wallpaper.jpg"
)
sidebar_bg_base64 = get_base64_of_image(
    r"C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\sidebarpng.png"
)

# Custom CSS for layout and theming
st.markdown(f"""
    <style>
    /* Main background */
    .stApp {{
        background-image: url("data:image/jpg;base64,{main_bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.85);
        z-index: -1;
    }}

    .main-title {{
        color: #2c3e50;
        text-align: center;
        padding: 15px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px auto 20px auto;
        width: fit-content;
        font-size: 32px;
        font-weight: bold;
    }}

    /* Rounded corners for plots */
    .element-container {{
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}

    .stPlotlyChart {{
        border-radius: 10px;
    }}

    /* Plot containers specifically */
    .element-container .stImage {{
        border-radius: 10px;
        overflow: hidden;
    }}

    .element-container .stPlotlyChart {{
        border-radius: 10px;
        overflow: hidden;
    }}

    /* Sidebar with solid black background */
    section[data-testid="stSidebar"] > div:first-child {{
        background-color: black;
        padding-top: 20px;
        padding-left: 10px;
        padding-right: 10px;
        height: 100%;
    }}

    /* Sidebar width */
    div[data-testid="stSidebar"] {{
        width: 250px !important;
    }}

    .sidebar-title h1, .sidebar-title h2, .sidebar-title h3 {{
        background: none !important;
        padding: 0 !important;
        margin-bottom: 10px !important;
        color: white !important;
        font-size: 22px !important;
    }}

    h1 {{
        color: #2c3e50;
        text-align: center;
        padding: 20px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}

    h2, h3 {{
        color: white;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-top: 20px;
        font-size: 27px;
    }}

    .stContainer {{
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }}

    .css-1d391kg {{
        background: rgba(255, 255, 255, 0.95);
    }}

    .hospital-card {{
        background: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        transition: transform 0.2s;
    }}

    .hospital-card:hover {{
        transform: translateY(-5px);
    }}

    .stButton>button {{
        background: #3498db;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        transition: background 0.3s;
    }}

    .stButton>button:hover {{
        background: #2980b9;
    }}

    ::-webkit-scrollbar {{
        width: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: #f1f1f1;
    }}

    ::-webkit-scrollbar-thumb {{
        background: #888;
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: #555;
    }}
    </style>
""", unsafe_allow_html=True)

# Add the main title
st.markdown('<h1 class="main-title">🤖 A.I for Disaster Relief</h1>', unsafe_allow_html=True)

# Custom-styled sidebar title
st.sidebar.markdown('<div class="sidebar-title"><h2>Select Disaster Area</h2></div>', unsafe_allow_html=True)

# Sidebar disaster selector
selected_disaster = st.sidebar.radio(
    "Choose a disaster area to analyze:",
    ["Joplin Tornado", "Sunda Tsunami"]
)

# Disaster summary KPIs
st.markdown("---", unsafe_allow_html=True)
st.markdown("""
    <style>
        .kpi-container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            padding: 20px 0;
            text-align: center;
        }
        .kpi {
            flex: 1;
            min-width: 150px;
            margin: 10px;
        }
        .kpi-title {
            font-size: 20px;
            color: #00bfff;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: white;
        }
        .kpi-wrapper {
            background: rgba(0, 0, 0, 0.4);
            padding: 15px;
            border-radius: 10px;
        }
        .summary-text {
            background: rgba(0, 0, 0, 0.5);
            color: white;
            text-align: center;
            font-size: 16px;
            padding: 12px 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: white; padding-bottom: 10px;'>🌍 Disaster Summary</h2>", unsafe_allow_html=True)

if selected_disaster == "Joplin Tornado":
    st.markdown("""
        <div class="kpi-container">
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">🌪️ Max Wind Speed</div>
                    <div class="kpi-value">210 mph</div>
                </div>
            </div>
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">💀 Fatalities</div>
                    <div class="kpi-value">158</div>
                </div>
            </div>
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">🩹 Injuries</div>
                    <div class="kpi-value">1,150+</div>
                </div>
            </div>
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">🏚️ Damage Estimate</div>
                    <div class="kpi-value">$2.8B</div>
                </div>
            </div>
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">📅 Date</div>
                    <div class="kpi-value">May 22, 2011</div>
                </div>
            </div>
        </div>

        <div class="summary-text">
            The Joplin EF5 tornado was one of the deadliest in U.S. history, with winds reaching 210 mph and causing over $2.8 billion in damage.
        </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div class="kpi-container">
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">🌊 Max Wave Height</div>
                    <div class="kpi-value">13 m</div>
                </div>
            </div>
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">💀 Fatalities</div>
                    <div class="kpi-value">437</div>
                </div>
            </div>
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">🩹 Injuries</div>
                    <div class="kpi-value">14,000+</div>
                </div>
            </div>
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">🧍‍♂️ Displaced People</div>
                    <div class="kpi-value">33,000+</div>
                </div>
            </div>
            <div class="kpi-wrapper">
                <div class="kpi">
                    <div class="kpi-title">📅 Date</div>
                    <div class="kpi-value">Dec 22, 2018</div>
                </div>
            </div>
        </div>

        <div class="summary-text">
            The 2018 Sunda Strait tsunami was triggered by an underwater volcanic eruption of Anak Krakatau, resulting in devastating waves and coastal destruction.
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Damage Assessment and Interactive Map
if selected_disaster == "Joplin Tornado":
    st.subheader("🌪️ Tornado Damage Assessment")
    st.markdown("""
    Interactive map showing the distribution and severity of tornado damage across Joplin.
    Color coding: 🟢 No damage | 🔵 Minor damage | 🟡 Major damage | 🔴 Destroyed
    """)

    # Read and display the Joplin HTML file
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\joplin_tornado_map.html', 'r', encoding='utf-8') as f:
        html_data = f.read()
    components.html(html_data, height=600)

else:
    st.subheader("🌊 Tsunami Damage Assessment")
    st.markdown("""
    Interactive map showing the distribution and severity of tsunami damage in the Sunda area.
    Color coding: 🟢 No damage | 🔵 Minor damage | 🟡 Major damage | 🔴 Destroyed
    """)

    # Read and display the Sunda HTML file
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda_tsunami_map.html', 'r', encoding='utf-8') as f:
        html_data = f.read()
    components.html(html_data, height=600)

st.markdown("---")

# Create three columns for the visualizations
col1, col2, col3 = st.columns(3)

if selected_disaster == "Joplin Tornado":
    # Joplin visualizations
    with col1:
        st.subheader("Population Density")
        st.markdown("Shows population distribution across Joplin, crucial for evacuation planning.")
        fig1 = create_population_density_map()
        fig1.set_size_inches(10, 16)
        st.pyplot(fig1)

    with col2:
        st.subheader("Elevation & POIs")
        st.markdown("Displays terrain elevation and important Points of Interest.")
        fig2 = create_elevation_poi_map()
        fig2.set_size_inches(10, 11)
        st.pyplot(fig2)

    with col3:
        st.subheader("Emergency Response Times")
        st.markdown("Visualizes estimated emergency response times across the city.")
        fig3 = create_response_time_map()
        fig3.set_size_inches(10, 11)
        st.pyplot(fig3)

else:
    # Sunda visualizations
    with col1:
        st.subheader("Population Density")
        st.markdown("Shows population distribution in the Sunda area, crucial for evacuation planning.")
        fig1 = create_sunda_population_density_map()
        fig1.set_size_inches(10, 10)
        st.pyplot(fig1)

    with col2:
        st.subheader("Elevation & POIs")
        st.markdown("Displays terrain elevation and important Points of Interest.")
        fig2 = create_sunda_elevation_map()
        fig2.set_size_inches(10, 10)
        st.pyplot(fig2)

    with col3:
        st.subheader("Emergency Response Times")
        st.markdown("Visualizes estimated emergency response times across the area.")
        fig3 = create_sunda_response_map()
        fig3.set_size_inches(10, 9)
        st.pyplot(fig3)

st.markdown("---")

# Satellite Images
if selected_disaster == "Joplin Tornado":
    st.subheader("🛰️ Satellite Images")
    st.markdown("Satellite images of the Joplin tornado damages.")
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\joplin_ok.png', 
                caption='First Image', use_column_width=True)
    
    with col2:
        st.image(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\joplin_chaos.png', 
                caption='Second Image', use_column_width=True)
else:
    st.subheader("🛰️ Satellite Images")
    st.markdown("Satellite images of the Sunda tsunami damages.")
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda_ok.png', 
                caption='First Image', use_column_width=True)
    
    with col2:
        st.image(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda_chaos.png', 
                caption='Second Image', use_column_width=True)

st.markdown("---")

# Damage Type Breakdown
if selected_disaster == "Joplin Tornado":
    st.subheader("📊 Damage Type Breakdown")
    st.markdown("This bar chart shows the distribution of damage types observed in the Joplin tornado.")
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\damage_type_barplot_joplin.html', 'r', encoding='utf-8') as f:
        joplin_damage_plot = f.read()
    components.html(joplin_damage_plot, height=600)

else:
    st.subheader("📊 Damage Type Breakdown")
    st.markdown("This bar chart shows the distribution of damage types observed in the Sunda tsunami.")
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\damage_type_barplot_suna.html', 'r', encoding='utf-8') as f:
        sunda_damage_plot = f.read()
    components.html(sunda_damage_plot, height=600)

st.markdown("---")

# Hospital Information
if selected_disaster == "Joplin Tornado":
    st.markdown("""
    <h2 style='color: white; padding-bottom: 10px;'>
        🏥 Hospital Information
    </h2>
        """, unsafe_allow_html=True)

    # Read Joplin hospital data
    with open(r'C:\Users\yanit\OneDrive\Bureau\AI_Disaster_Relief\app\responsetime\hospitals_joplin.geojson', 'r') as f:
        hospitals_data = json.load(f)

    # Create columns for each hospital
    cols = st.columns(len(hospitals_data['features']))

    for idx, hospital in enumerate(hospitals_data['features']):
        with cols[idx]:
            name = hospital['properties'].get('name', 'N/A')
            address = f"{hospital['properties'].get('addr:housenumber', 'N/A')} {hospital['properties'].get('addr:street', 'N/A')}"
            city_zip = f"{hospital['properties'].get('addr:city', 'N/A')}, {hospital['properties'].get('addr:postcode', 'N/A')}"
            phone = hospital['properties'].get('phone', 'N/A')
            website = hospital['properties'].get('website', '#')
            beds = hospital['properties'].get('beds', 'N/A')
            
            facilities = []
            if hospital['properties'].get('helipad') == 'yes':
                facilities.append("🚁 Helipad Available")
            if hospital['properties'].get('emergency') == 'yes':
                facilities.append("🏥 Emergency Services")
            if beds != 'N/A':
                facilities.append(f"🛏️ Beds: {beds}")

            st.subheader(name)
            st.markdown("**Address**")
            st.text(address)
            st.text(city_zip)
            st.markdown("**Contact**")
            st.text(f"📞 {phone}")
            st.markdown("**Facilities**")
            if facilities:
                for facility in facilities:
                    st.text(facility)
            else:
                st.text("No facility information available")
            st.markdown("**Website**")
            st.markdown(f"[Visit Website]({website})")

else:
    st.markdown("""
    <h2 style='color: white; padding-bottom: 10px;'>
        🏥 Hospital Information
    </h2>
        """, unsafe_allow_html=True)

    # Read Sunda hospital data
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda_hospital.geojson', 'r') as f:
        hospitals_data = json.load(f)

    # Create columns for each hospital
    cols = st.columns(len(hospitals_data['features']))

    for idx, hospital in enumerate(hospitals_data['features']):
        with cols[idx]:
            name = hospital['properties'].get('name', 'N/A')
            address = f"{hospital['properties'].get('addr:housenumber', 'N/A')} {hospital['properties'].get('addr:street', 'N/A')}"
            city_zip = f"{hospital['properties'].get('addr:city', 'N/A')}, {hospital['properties'].get('addr:postcode', 'N/A')}"
            phone = hospital['properties'].get('phone', 'N/A')
            website = hospital['properties'].get('website', '#')
            beds = hospital['properties'].get('beds', 'N/A')
            
            facilities = []
            if hospital['properties'].get('helipad') == 'yes':
                facilities.append("🚁 Helipad Available")
            if hospital['properties'].get('emergency') == 'yes':
                facilities.append("🏥 Emergency Services")
            if beds != 'N/A':
                facilities.append(f"🛏️ Beds: {beds}")

            st.subheader(name)
            st.markdown("**Address**")
            st.text(address)
            st.text(city_zip)
            st.markdown("**Contact**")
            st.text(f"📞 {phone}")
            st.markdown("**Facilities**")
            if facilities:
                for facility in facilities:
                    st.text(facility)
            else:
                st.text("No facility information available")
            st.markdown("**Website**")
            st.markdown(f"[Visit Website]({website})") 