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
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Encode main background
main_bg_base64 = get_base64_of_image(
    r"C:/Users/yanit/OneDrive/Bureau/Data Insights And Visualization/wallpaperflare.com_wallpaper.jpg"
)

# Custom CSS
st.markdown(f"""
    <style>
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
    section[data-testid="stSidebar"] > div:first-child {{
        background-color: black;
        padding-top: 20px;
        padding-left: 10px;
        padding-right: 10px;
        height: 100%;
    }}
    div[data-testid="stSidebar"] {{
        width: 250px !important;
    }}
    .sidebar-title h1, .sidebar-title h2, .sidebar-title h3 {{
        background: none !important;
        padding: 0 !important;
        margin-bottom: 10px !important;
        color: white !important;
        font-size: 22px !important;
        text-decoration: underline;
    }}
    .kpi-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background: rgba(0, 0, 0, 0.6);
        border-radius: 10px;
        color: white;
        margin-top: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }}
    .kpi-box {{
        flex: 1;
        min-width: 150px;
        text-align: center;
        padding: 10px;
    }}
    .kpi-box .kpi-label {{
        font-size: 18px;
        color: #00bfff;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }}
    .kpi-box .kpi-value {{
        font-size: 26px;
        font-weight: bold;
    }}
    .kpi-title-header {{
        font-size: 28px;
        color: white;
        padding: 10px 0;
        border-bottom: 2px solid #00bfff;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-title"><h2>Select Disaster Area</h2></div>', unsafe_allow_html=True)
selected_disaster = st.sidebar.radio("Choose a disaster area to analyze:", ["Joplin Tornado", "Sunda Tsunami"])

# DISASTER SUMMARY (Updated)
st.markdown("""
<div class="kpi-title-header">🌍 Disaster Summary
</div>
""", unsafe_allow_html=True)

if selected_disaster == "Joplin Tornado":
    st.markdown("""
    <div class="kpi-row">
        <div class="kpi-box">
            <div class="kpi-label">🚨 Max Wind Speed</div>
            <div class="kpi-value">210 mph</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">☠️ Fatalities</div>
            <div class="kpi-value">158</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">💉 Injuries</div>
            <div class="kpi-value">1,150+</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">🏠 Damage Estimate</div>
            <div class="kpi-value">$2.8B</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">🗓️ Date</div>
            <div class="kpi-value">May 22, 2011</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="kpi-row">
        <div class="kpi-box">
            <div class="kpi-label">🌊 Max Wave Height</div>
            <div class="kpi-value">13 m</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">☠️ Fatalities</div>
            <div class="kpi-value">437</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">💉 Injuries</div>
            <div class="kpi-value">14,000+</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">🧐 Displaced People</div>
            <div class="kpi-value">33,000+</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">🗓️ Date</div>
            <div class="kpi-value">Dec 22, 2018</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# INTERACTIVE MAP
st.markdown("---")
if selected_disaster == "Joplin Tornado":
    st.subheader("Tornado Damage Assessment")
    st.markdown("""Interactive map showing the distribution and severity of tornado damage across Joplin.
    Color coding: 🟢 No damage | 🔵 Minor damage | 🟡 Major damage | 🔴 Destroyed""")
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\joplin_tornado_map.html', 'r', encoding='utf-8') as f:
        html_data = f.read()
    components.html(html_data, height=600)
else:
    st.subheader("Tsunami Damage Assessment")
    st.markdown("""Interactive map showing the distribution and severity of tsunami damage in the Sunda area.
    Color coding: 🟢 No damage | 🔵 Minor damage | 🟡 Major damage | 🔴 Destroyed""")
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda_tsunami_map.html', 'r', encoding='utf-8') as f:
        html_data = f.read()
    components.html(html_data, height=600)

# THREE MAPS
st.markdown("---")
col1, col2, col3 = st.columns(3)
if selected_disaster == "Joplin Tornado":
    with col1:
        st.subheader("Population Density")
        st.markdown("Shows population distribution across Joplin, crucial for evacuation planning.")
        fig1 = create_population_density_map()
        fig1.set_size_inches(10, 10)
        st.pyplot(fig1)
    with col2:
        st.subheader("Elevation & POIs")
        st.markdown("Displays terrain elevation and important Points of Interest.")
        fig2 = create_elevation_poi_map()
        fig2.set_size_inches(10, 10)
        st.pyplot(fig2)
    with col3:
        st.subheader("Emergency Response Times")
        st.markdown("Visualizes estimated emergency response times across the city.")
        fig3 = create_response_time_map()
        fig3.set_size_inches(10, 10)
        st.pyplot(fig3)
else:
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
        fig3.set_size_inches(10, 10)
        st.pyplot(fig3)

# DAMAGE TYPE BAR CHART
st.markdown("---")
if selected_disaster == "Joplin Tornado":
    st.subheader("📊 Damage Type Breakdown")
    st.markdown("This bar chart shows the distribution of damage types observed in the Joplin tornado.")
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\damage_type_barplot_joplin.html', 'r', encoding='utf-8') as f:
        damage_chart = f.read()
    components.html(damage_chart, height=600)
else:
    st.subheader("📊 Damage Type Breakdown")
    st.markdown("This bar chart shows the distribution of damage types observed in the Sunda tsunami.")
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\damage_type_barplot_suna.html', 'r', encoding='utf-8') as f:
        damage_chart = f.read()
    components.html(damage_chart, height=600)

# SATELLITE IMAGES
st.markdown("---")
st.subheader("Satellite Images")
if selected_disaster == "Joplin Tornado":
    st.markdown("Satellite images of the Joplin tornado damages.")
    col1, col2 = st.columns(2)
    with col1:
        st.image(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\joplin_ok.png', caption='First Image', use_column_width=True)
    with col2:
        st.image(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\joplin_chaos.png', caption='Second Image', use_column_width=True)
else:
    st.markdown("Satellite images of the Sunda tsunami damages.")
    col1, col2 = st.columns(2)
    with col1:
        st.image(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda_ok.png', caption='First Image', use_column_width=True)
    with col2:
        st.image(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda_chaos.png', caption='Second Image', use_column_width=True)

st.markdown("---")
st.markdown("""
<h2 style='color: white; padding-bottom: 10px;'>🏥 Hospital Information</h2>
""", unsafe_allow_html=True)

if selected_disaster == "Joplin Tornado":
    with open('responsetime/hospitals_joplin.geojson', 'r') as f:
        hospitals_data = json.load(f)
else:
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda_hospital.geojson', 'r') as f:
        hospitals_data = json.load(f)

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
            facilities.append(f"🛌 Beds: {beds}")

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

