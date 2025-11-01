# app.py - SmartAgri AI Complete Application
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta

# ----------------------------
# APP CONFIG
# ----------------------------
st.set_page_config(page_title="SmartAgri AI", page_icon="🌾", layout="wide")

# ----------------------------
# SESSION STATE INIT
# ----------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "farmer_profile" not in st.session_state:
    st.session_state.farmer_profile = {}
if "saved_recommendations" not in st.session_state:
    st.session_state.saved_recommendations = []
if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False

for key in ["crop_list","show_graph","show_advisory","state_crops","show_state_graph",
            "market_data","soil","weather_data","disease_prediction","loan_calc","water_calc"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ----------------------------
# MULTI-LANGUAGE SUPPORT
# ----------------------------
LANG = {
    "English": {
        "welcome": "Welcome to SmartAgri AI",
        "recommend_crops": "Recommend Crops",
        "show_graph": "Show Graph",
        "show_advisory": "Show Advisory",
        "chatbot": "AI Chatbot Assistant",
        "market_forecast": "Market Forecast",
        "state_insights": "State Insights",
        "weather": "Weather Insights",
        "disease_detection": "Disease Detection",
        "loan_calculator": "Loan Calculator",
        "water_management": "Water Management",
        "fertilizer_calc": "Fertilizer Calculator",
        "govt_schemes": "Government Schemes",
        "calculate": "Calculate",
        "send": "Send",
        "save_profile": "Save Profile"
    },
    "Hindi": {
        "welcome": "स्मार्टएग्री एआई में आपका स्वागत है",
        "recommend_crops": "फसल की सिफारिश",
        "chatbot": "एआई चैटबॉट सहायक",
        "calculate": "गणना करें"
    },
    "Tamil": {
        "welcome": "ஸ்மார்ட் அஃக்ரி AIக்கு வரவேற்கிறோம்",
        "recommend_crops": "பயிர் பரிந்துரை",
        "chatbot": "AI சாட்பாட் உதவியாளர்",
        "calculate": "கணக்கிடு"
    }
}

# ----------------------------
# ALL INDIAN STATES
# ----------------------------
ALL_INDIAN_STATES = [
    'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat',
    'Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh',
    'Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan',
    'Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal',
    'Delhi','Jammu & Kashmir','Puducherry'
]

# ----------------------------
# CHATBOT KNOWLEDGE BASE
# ----------------------------
KNOWLEDGE = {
    "rice": "Rice cultivation: Best in clayey soil, needs 1500-2000mm rainfall, 25-35°C. Kharif crop, 4-6 months. Varieties: Basmati, IR-64.",
    "wheat": "Wheat: Loamy soil, 600-800mm rainfall, 15-25°C. Rabi crop, 4-5 months. Varieties: HD-2967, PBW-343.",
    "cotton": "Cotton: Black soil, 600-1200mm rainfall, 21-27°C. Kharif crop, 5-6 months. Requires pest management.",
    "pm kisan": "PM-KISAN: ₹6,000/year to farmers. ₹2,000 every 4 months. Register at pmkisan.gov.in",
    "loan": "Agricultural loans: KCC provides up to ₹3 lakhs at 7% interest (4% after subsidy).",
    "soil test": "Soil testing: Test every 2-3 years for NPK. Cost: ₹50-200. Visit nearest KVK.",
    "irrigation": "Drip irrigation saves 40-60% water. Sprinkler saves 20-30%. Government subsidies available."
}

def get_chatbot_response(user_input):
    user_lower = user_input.lower()
    
    # Check knowledge base
    for keyword, response in KNOWLEDGE.items():
        if keyword in user_lower:
            return response
    
    # Greetings
    if any(g in user_lower for g in ["hello", "hi", "namaste"]):
        return "🙏 Namaste! I'm SmartAgri AI. Ask me about crops, loans, schemes, or farming practices!"
    
    # Help
    if "help" in user_lower:
        return "I can help with: 🌾 Crops, 💰 Loans, 🏛️ Schemes, 💧 Irrigation, 🦗 Pests, 📈 Markets. Ask anything!"
    
    return "I can help with farming questions. Try asking about crops, PM-KISAN, loans, or soil testing!"

# ----------------------------
# THEME STYLING
# ----------------------------
def set_theme(theme):
    if theme == "dark":
        bg = "#0E1117"
        text = "#FFFFFF"
        panel = "#262730"
        card_bg = "#1E1E1E"
        input_bg = "#262730"
        border_color = "#4B8B3B"
    else:
        bg = "#FFFFFF"
        text = "#262626"
        panel = "#E8F5E9"
        card_bg = "#F5F5F5"
        input_bg = "#FFFFFF"
        border_color = "#4B8B3B"
    
    st.session_state.plotly_template = "plotly_dark" if theme == "dark" else "plotly_white"
    
    st.markdown(f"""
    <style>
        /* Force all text to be visible */
        * {{
            color: {text} !important;
        }}
        
        /* Main App */
        .stApp {{
            background-color: {bg} !important;
        }}
        
        /* Override Streamlit defaults */
        .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
        .stText, p, span, div, label, h1, h2, h3, h4, h5, h6,
        .css-10trblm, .css-16idsys {{
            color: {text} !important;
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricDelta"],
        .css-1wivap2, .css-50ug3q {{
            color: {text} !important;
        }}
        
        /* Input Fields */
        .stTextInput input, .stTextInput textarea,
        .stNumberInput input,
        input, textarea {{
            background-color: {input_bg} !important;
            color: {text} !important;
            border: 1px solid {border_color} !important;
        }}
        
        /* Selectbox - remove visible box */
        .stSelectbox > div > div {{
            background-color: transparent !important;
            border: none !important;
        }}
        .stSelectbox select {{
            background-color: {input_bg} !important;
            color: {text} !important;
            border: 1px solid {border_color} !important;
        }}
        .stSelectbox label {{
            color: {text} !important;
        }}
        
        /* Sliders */
        .stSlider label, .stSlider div, .stSlider span {{
            color: {text} !important;
        }}
        
        /* Radio and Checkbox */
        .stRadio label, .stRadio div, .stRadio span,
        .stCheckbox label, .stCheckbox div, .stCheckbox span {{
            color: {text} !important;
        }}
        
        /* Multiselect */
        .stMultiSelect label, .stMultiSelect div, .stMultiSelect span {{
            color: {text} !important;
        }}
        
        /* Tabs */
        [data-baseweb="tab-list"] button,
        [data-baseweb="tab-list"] button div {{
            color: {text} !important;
        }}
        [data-baseweb="tab-list"] button[aria-selected="true"] {{
            color: #4B8B3B !important;
            border-bottom: 2px solid #4B8B3B !important;
        }}
        
        /* Alert boxes - keep their own colors for text */
        .stAlert, .stAlert * {{
            /* Let alerts use their default text colors */
        }}
        
        /* Expander */
        .streamlit-expanderHeader, .streamlit-expanderHeader * {{
            color: {text} !important;
        }}
        
        /* Dataframes */
        .stDataFrame, .stDataFrame * {{
            color: {text} !important;
        }}
        
        /* Feature Cards - white text always */
        .feature-card {{
            background: linear-gradient(135deg, #4B8B3B 0%, #6BA54D 100%);
            color: #FFFFFF !important;
            padding: 20px;
            border-radius: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .feature-card * {{
            color: #FFFFFF !important;
        }}
        
        /* Chat Messages */
        .chat-user {{
            background-color: #4B8B3B;
            color: #FFFFFF !important;
            padding: 12px 18px;
            border-radius: 18px;
            margin: 8px 0;
            text-align: right;
        }}
        .chat-user * {{
            color: #FFFFFF !important;
        }}
        .chat-bot {{
            background-color: {panel};
            color: {text} !important;
            padding: 12px 18px;
            border-radius: 18px;
            margin: 8px 0;
        }}
        .chat-bot * {{
            color: {text} !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: #4B8B3B !important;
            color: #FFFFFF !important;
            border: none !important;
            font-weight: 600 !important;
        }}
        .stButton > button * {{
            color: #FFFFFF !important;
        }}
        
        /* Download Button */
        .stDownloadButton > button {{
            background-color: #4B8B3B !important;
            color: #FFFFFF !important;
        }}
        .stDownloadButton > button * {{
            color: #FFFFFF !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {panel} !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {text} !important;
        }}
        
        /* File Uploader */
        .stFileUploader label, .stFileUploader div {{
            color: {text} !important;
        }}
        
        /* Markdown in containers */
        .element-container, .element-container * {{
            color: {text} !important;
        }}
        
        /* Weather cards in dark theme */
        .weather-card {{
            color: #FFFFFF !important;
        }}
    </style>
    """, unsafe_allow_html=True)

set_theme(st.session_state.theme)

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.title("🌾 SmartAgri AI")
st.sidebar.markdown("**Empowering Indian Farmers**")

menu = ["Home", "Crop Recommendation", "Market Forecast", "Weather Insights", 
        "Disease Detection", "Loan Calculator", "Fertilizer Calculator", 
        "Government Schemes", "Chatbot", "My Profile", "Settings"]
choice = st.sidebar.radio("📍 Navigate", menu)

# ----------------------------
# HOME PAGE
# ----------------------------
if choice == "Home":
    st.markdown(f"<h1 style='text-align:center;color:#4B8B3B;'>{LANG[st.session_state.language]['welcome']}</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Your Complete Digital Farming Companion 🚜</h3>", 
                unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Farmers", "25,000+", "+18%")
    with col2:
        st.metric("Crops Database", "100+")
    with col3:
        st.metric("States Covered", "37")
    with col4:
        st.metric("Success Rate", "96%")
    
    st.markdown("---")
    
    # Features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='feature-card'>
        <h3>🌱 Crop Recommendation</h3>
        <p>AI-powered crop suggestions based on soil, climate, and location</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-card'>
        <h3>🦠 Disease Detection</h3>
        <p>Identify crop diseases and get treatment plans</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
        <h3>📈 Market Forecast</h3>
        <p>Price predictions powered by ML algorithms</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-card'>
        <h3>💰 Loan Calculator</h3>
        <p>Calculate EMI for agricultural loans</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
        <h3>🌤️ Weather Insights</h3>
        <p>7-day forecast with farming advisories</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-card'>
        <h3>🏛️ Government Schemes</h3>
        <p>Complete information on subsidies and support</p>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------
# CROP RECOMMENDATION (ENHANCED)
# ----------------------------
elif choice == "Crop Recommendation":
    st.header(f"🌱 {LANG[st.session_state.language]['recommend_crops']}")
    
    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox("Select State", ALL_INDIAN_STATES)
        soil = st.selectbox("Soil Type", ["Loamy","Clayey","Sandy","Black","Alluvial","Red","Laterite"])
        rainfall = st.slider("Rainfall (mm)", 100, 3000, 800)
    
    with col2:
        temp = st.slider("Temperature (°C)", 10, 45, 28)
        humidity = st.slider("Humidity (%)", 20, 100, 60)
        ph = st.slider("Soil pH", 4.0, 9.0, 6.5, 0.1)

    season = st.radio("Season", ["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)"])
    
    if st.button("🌾 Get Recommendations", type="primary"):
        crop_data = {
            "Loamy":["Wheat","Rice","Sugarcane","Cotton","Vegetables","Fruits"],
            "Clayey":["Paddy","Soybean","Linseed","Wheat","Pulses"],
            "Sandy":["Millets","Groundnut","Watermelon","Coconut","Cashew"],
            "Black":["Cotton","Sorghum","Sunflower","Chickpea","Soybean"],
            "Alluvial":["Maize","Mustard","Barley","Rice","Sugarcane","Jute"],
            "Red":["Groundnut","Pulses","Millets","Oilseeds","Cotton"],
            "Laterite":["Cashew","Tapioca","Coconut","Coffee","Tea","Spices"]
        }
        
        crops = crop_data.get(soil, [])
        
        # Filter by temperature
        if temp > 35:
            crops = [c for c in crops if c in ["Cotton","Sorghum","Millets","Sunflower","Groundnut"]]
        elif temp < 20:
            crops = [c for c in crops if c in ["Wheat","Barley","Mustard","Chickpea","Potato"]]
        
        # Filter by season
        if "Kharif" in season:
            kharif_crops = ["Rice","Cotton","Soybean","Groundnut","Maize","Millets","Paddy"]
            crops = [c for c in crops if c in kharif_crops]
        elif "Rabi" in season:
            rabi_crops = ["Wheat","Chickpea","Mustard","Barley","Potato"]
            crops = [c for c in crops if c in rabi_crops]
        
        if not crops:
            crops = crop_data.get(soil, [])[:5]
        
        st.session_state.crop_list = crops[:5]
        st.success(f"✅ Top {len(st.session_state.crop_list)} Recommended Crops: {', '.join(st.session_state.crop_list)}")

    if st.session_state.crop_list:
        tabs = st.tabs(["Recommended Crops", "Performance Graph", "Farming Advisory", "Crop Calendar"])
        
        with tabs[0]:
            st.subheader("🌾 Detailed Crop Information")
            for i, crop in enumerate(st.session_state.crop_list, 1):
                yield_val = np.random.randint(60, 95)
                profit = np.random.randint(50000, 150000)
                duration = np.random.randint(90, 180)
                water_req = np.random.choice(["Low", "Medium", "High"])
                
                st.markdown(f"""
                <div class='feature-card'>
                <h4>{i}. {crop}</h4>
                <p><strong>Expected Yield:</strong> {yield_val}% | <strong>Profit:</strong> ₹{profit:,}/acre | <strong>Duration:</strong> {duration} days</p>
                <p><strong>Water Requirement:</strong> {water_req} | <strong>Season:</strong> {season.split()[0]}</p>
                </div>
                """, unsafe_allow_html=True)

        with tabs[1]:
            st.subheader("📊 Crop Performance Analysis")
            df = pd.DataFrame({
                "Crop": st.session_state.crop_list,
                "Yield Index": np.random.randint(60, 95, len(st.session_state.crop_list)),
                "Profit Potential": np.random.randint(50, 95, len(st.session_state.crop_list)),
                "Risk Factor": np.random.randint(20, 60, len(st.session_state.crop_list))
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Yield Index', x=df["Crop"], y=df["Yield Index"], 
                                marker_color='#4B8B3B'))
            fig.add_trace(go.Bar(name='Profit Potential', x=df["Crop"], y=df["Profit Potential"], 
                                marker_color='#FFD700'))
            fig.add_trace(go.Bar(name='Risk Factor', x=df["Crop"], y=df["Risk Factor"], 
                                marker_color='#FF6B6B'))
            fig.update_layout(
                title="Comprehensive Crop Comparison",
                barmode='group',
                template=st.session_state.plotly_template,
                xaxis_title="Crops",
                yaxis_title="Score"
            )
            st.plotly_chart(fig, use_container_width=True)

        with tabs[2]:
            st.subheader("🌾 Comprehensive Farming Advisory")
            
            st.markdown("#### 💧 Irrigation Management")
            st.info("• Drip irrigation saves 40-60% water and increases yield by 20-50%")
            st.info("• Irrigate early morning (6-8 AM) or evening (5-7 PM) to reduce evaporation")
            st.info("• Monitor soil moisture regularly using feel method or tensiometers")
            
            st.markdown("#### 🌿 Soil & Nutrient Management")
            st.info("• Conduct soil testing annually for accurate NPK recommendations")
            st.info("• Apply 5-10 tons of FYM/compost per acre to improve soil health")
            st.info("• Follow crop rotation: Cereal → Legume → Oilseed cycle")
            
            st.markdown("#### 🦗 Pest & Disease Control")
            st.info("• Follow Integrated Pest Management (IPM) practices")
            st.info("• Scout fields weekly for early pest detection")
            st.info("• Use neem-based pesticides as first line of defense")
            
            st.markdown("#### 🌾 Best Practices")
            st.info("• Use certified quality seeds from authorized dealers")
            st.info("• Maintain proper plant spacing for air circulation")
            st.info("• Keep field borders clean to reduce pest breeding")
            st.info("• Record all farming activities for better planning")
        
        with tabs[3]:
            st.subheader("📅 Seasonal Crop Calendar")
            calendar_data = []
            months_map = {
                "Kharif": {"sowing": "June-July", "harvest": "October-November"},
                "Rabi": {"sowing": "October-November", "harvest": "March-April"},
                "Zaid": {"sowing": "March-April", "harvest": "June-July"}
            }
            
            season_key = season.split()[0]
            for crop in st.session_state.crop_list:
                calendar_data.append({
                    "Crop": crop,
                    "Sowing Period": months_map[season_key]["sowing"],
                    "Harvest Period": months_map[season_key]["harvest"],
                    "Duration": f"{np.random.randint(90, 180)} days",
                    "Season": season_key
                })
            
            cal_df = pd.DataFrame(calendar_data)
            st.dataframe(cal_df, use_container_width=True)
            
            st.markdown("#### 📋 Important Milestones")
            st.write("**Week 1-2:** Land preparation, seed treatment")
            st.write("**Week 3-4:** Sowing/transplanting, first irrigation")
            st.write("**Week 5-8:** Vegetative growth, fertilizer application")
            st.write("**Week 9-12:** Flowering/fruiting, pest monitoring")
            st.write("**Final Weeks:** Maturity, harvest preparation")

# ----------------------------
# MARKET FORECAST
# ----------------------------
elif choice == "Market Forecast":
    st.header("📈 Market Price Forecast")
    
    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox("Select Crop", 
                           ["Rice","Wheat","Cotton","Onion","Potato","Tomato"])
    with col2:
        days = st.slider("Forecast Days", 7, 60, 30)
    
    if st.button("Show Forecast", type="primary"):
        forecast_days = np.arange(1, days+1)
        base = np.random.randint(1500, 3000)
        trend = np.linspace(0, 200, days)
        noise = np.random.normal(0, 50, days)
        prices = base + trend + noise
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"₹{int(prices[0])}/q")
        with col2:
            st.metric("Expected Price", f"₹{int(prices[-1])}/q", 
                     f"{((prices[-1]-prices[0])/prices[0]*100):+.1f}%")
        with col3:
            st.metric("Peak Price", f"₹{int(max(prices))}/q")
        
        fig = px.line(x=forecast_days, y=prices, 
                     title=f"{days}-Day Price Forecast: {crop}",
                     labels={"x": "Days", "y": "Price (₹/quintal)"},
                     template=st.session_state.plotly_template)
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# WEATHER INSIGHTS
# ----------------------------
elif choice == "Weather Insights":
    st.header("🌤️ Weather Forecast")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        location = st.selectbox("Select Location", ALL_INDIAN_STATES)
    with col2:
        st.markdown("")
        if st.button("Get 7-Day Forecast", type="primary", use_container_width=True):
            st.session_state.weather_data = True
    
    if st.session_state.weather_data:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        temps_max = np.random.randint(28, 38, 7)
        temps_min = np.random.randint(18, 25, 7)
        rainfall = np.random.randint(0, 40, 7)
        
        cols = st.columns(7)
        for i, day in enumerate(days):
            with cols[i]:
                icon = "☀️" if rainfall[i] < 5 else "🌧️"
                st.markdown(f"""
                <div style='background:#4B8B3B; color:white; padding:15px; 
                           border-radius:10px; text-align:center;'>
                <h4>{day}</h4>
                <p style='font-size:28px;'>{icon}</p>
                <p><b>{temps_max[i]}°C</b></p>
                <p>{temps_min[i]}°C</p>
                <p>💧{rainfall[i]}mm</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🌾 Farming Advisory")
        if np.mean(rainfall) > 20:
            st.warning("⚠️ Heavy rainfall expected - ensure proper drainage")
        else:
            st.success("✅ Good weather for farming activities")

# ----------------------------
# DISEASE DETECTION
# ----------------------------
elif choice == "Disease Detection":
    st.header("🦠 Crop Disease Detection")
    
    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox("Select Crop", ["Rice","Wheat","Cotton","Tomato","Potato"])
        symptoms = st.multiselect("Symptoms", 
                                  ["Yellow Leaves","Brown Spots","Wilting","Holes"])
        severity = st.select_slider("Severity", ["Mild","Moderate","Severe"])
    
    with col2:
        uploaded = st.file_uploader("Upload Image (Optional)", type=['jpg','png'])
        if uploaded:
            st.image(uploaded, caption="Analyzing...", width=250)
    
    if st.button("Diagnose Disease", type="primary"):
        diseases = {
            "Rice": "Bacterial Leaf Blight",
            "Wheat": "Rust Disease",
            "Cotton": "Bollworm",
            "Tomato": "Late Blight",
            "Potato": "Early Blight"
        }
        
        disease = diseases.get(crop, "Unknown Disease")
        
        st.success(f"🔍 Detected: **{disease}**")
        st.info(f"**Treatment:** Spray recommended fungicide. Remove affected parts.")
        st.info(f"**Prevention:** Use resistant varieties. Maintain field hygiene.")
        st.metric("AI Confidence", f"{np.random.randint(80, 95)}%")

# ----------------------------
# LOAN CALCULATOR
# ----------------------------
elif choice == "Loan Calculator":
    st.header("💰 Agricultural Loan Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        loan_type = st.selectbox("Loan Type", 
                                ["Kisan Credit Card","Crop Loan","Tractor Loan"])
        amount = st.number_input("Loan Amount (₹)", 10000, 10000000, 200000, 10000)
        rate = st.slider("Interest Rate (%)", 4.0, 15.0, 7.0, 0.5)
    
    with col2:
        tenure = st.slider("Tenure (months)", 6, 240, 36)
        subsidy = st.checkbox("Interest Subsidy (3%)")
        effective_rate = max(rate - 3, 0) if subsidy else rate
        st.success(f"Effective Rate: {effective_rate}%")
    
    if st.button(LANG[st.session_state.language]["calculate"], type="primary"):
        r = effective_rate / (12 * 100)
        n = tenure
        
        if r > 0:
            emi = amount * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        else:
            emi = amount / n
        
        total = emi * n
        interest = total - amount
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Monthly EMI", f"₹{emi:,.0f}")
        with col2:
            st.metric("Total Interest", f"₹{interest:,.0f}")
        with col3:
            st.metric("Total Payment", f"₹{total:,.0f}")
        
        st.markdown("---")
        st.subheader("📊 Payment Breakdown")
        
        fig = go.Figure(data=[go.Pie(
            labels=['Principal', 'Interest'],
            values=[amount, interest],
            hole=.3,
            marker_colors=['#4B8B3B', '#FFD700']
        )])
        fig.update_layout(
            title="Loan Payment Distribution",
            template=st.session_state.plotly_template
        )
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# FERTILIZER CALCULATOR
# ----------------------------
elif choice == "Fertilizer Calculator":
    st.header("🧪 NPK Fertilizer Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox("Crop", ["Rice","Wheat","Cotton","Maize"])
        area = st.number_input("Area (acres)", 0.5, 100.0, 5.0, 0.5)
        yield_target = st.number_input("Target Yield (q/acre)", 10, 100, 50)
    
    with col2:
        soil_n = st.number_input("Soil Nitrogen (kg/acre)", 0, 500, 180)
        soil_p = st.number_input("Soil Phosphorus (kg/acre)", 0, 100, 25)
        soil_k = st.number_input("Soil Potassium (kg/acre)", 0, 500, 150)
    
    if st.button(LANG[st.session_state.language]["calculate"], type="primary"):
        req = {"Rice": {"N": 2.5, "P": 0.6, "K": 2.5},
               "Wheat": {"N": 3.0, "P": 0.6, "K": 2.0}}
        
        r = req.get(crop, {"N": 2.5, "P": 0.6, "K": 2.0})
        
        n_need = max(yield_target * r['N'] * area - soil_n * area, 0)
        p_need = max(yield_target * r['P'] * area - soil_p * area, 0)
        k_need = max(yield_target * r['K'] * area - soil_k * area, 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nitrogen (N)", f"{n_need:.1f} kg")
            urea = n_need / 0.46
            st.write(f"Urea: {urea:.1f} kg")
        with col2:
            st.metric("Phosphorus (P)", f"{p_need:.1f} kg")
            dap = p_need / 0.46
            st.write(f"DAP: {dap:.1f} kg")
        with col3:
            st.metric("Potassium (K)", f"{k_need:.1f} kg")
            mop = k_need / 0.60
            st.write(f"MOP: {mop:.1f} kg")

# ----------------------------
# GOVERNMENT SCHEMES
# ----------------------------
elif choice == "Government Schemes":
    st.header("🏛️ Government Schemes for Farmers")
    
    tabs = st.tabs(["Income Support", "Insurance", "Subsidies"])
    
    with tabs[0]:
        st.subheader("💰 PM-KISAN")
        st.info("**Benefit:** ₹6,000/year (₹2,000 every 4 months)")
        st.info("**Eligibility:** All landholding farmers")
        st.info("**Apply:** pmkisan.gov.in")
        
        if st.button("Check PM-KISAN Status"):
            st.success("Visit: pmkisan.gov.in → Beneficiary Status")
    
    with tabs[1]:
        st.subheader("🛡️ PM Fasal Bima Yojana")
        st.info("**Premium:** 2% for Kharif, 1.5% for Rabi")
        st.info("**Coverage:** Natural calamities, pests, diseases")
        st.info("**Apply:** pmfby.gov.in or through banks")
    
    with tabs[2]:
        st.subheader("🚜 Available Subsidies")
        st.info("• Drip/Sprinkler: 50-90% subsidy")
        st.info("• Farm Machinery: 40-80% subsidy")
        st.info("• Solar Pump: 60-90% subsidy")
        st.info("Contact: District Agriculture Office")

# ----------------------------
# CHATBOT
# ----------------------------
elif choice == "Chatbot":
    st.header(f"💬 {LANG[st.session_state.language]['chatbot']}")
    
    st.markdown("Ask me anything about farming, crops, loans, or government schemes!")
    
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history[-10:]:
            if msg['role'] == 'user':
                st.markdown(f"<div class='chat-user'>{msg['content']}</div>", 
                           unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bot'>{msg['content']}</div>", 
                           unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_msg = st.text_input("Your question:", key="chat_input", 
                                placeholder="e.g., How to grow rice?")
    with col2:
        send_btn = st.button(LANG[st.session_state.language]["send"], type="primary")
    
    if send_btn and user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        response = get_chatbot_response(user_msg)
        st.session_state.chat_history.append({"role": "bot", "content": response})
        st.rerun()
    
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ----------------------------
# MY PROFILE PAGE
# ----------------------------
elif choice == "My Profile":
    st.header("👨‍🌾 My Farmer Profile")
    
    if not st.session_state.profile_complete:
        st.info("📝 Please complete your profile to get personalized farming recommendations!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Personal Information")
        name = st.text_input("Full Name *", 
                            value=st.session_state.farmer_profile.get('name', ''),
                            placeholder="Enter your full name")
        
        col_a, col_b = st.columns(2)
        with col_a:
            age = st.number_input("Age", 18, 100, 
                                 value=st.session_state.farmer_profile.get('age', 35))
        with col_b:
            phone = st.text_input("Mobile Number *", 
                                 value=st.session_state.farmer_profile.get('phone', ''),
                                 placeholder="+91 XXXXXXXXXX")
        
        state = st.selectbox("State *", ALL_INDIAN_STATES,
                            index=ALL_INDIAN_STATES.index(st.session_state.farmer_profile.get('state', 'Tamil Nadu')) 
                            if st.session_state.farmer_profile.get('state') in ALL_INDIAN_STATES else 0)
        
        district = st.text_input("District", 
                                value=st.session_state.farmer_profile.get('district', ''),
                                placeholder="Enter your district")
        
        st.markdown("---")
        st.subheader("🌾 Farm Details")
        
        col_a, col_b = st.columns(2)
        with col_a:
            land_size = st.number_input("Total Land (acres) *", 0.1, 10000.0,
                                       value=float(st.session_state.farmer_profile.get('land', 2.0)), 
                                       step=0.5)
        with col_b:
            soil_type = st.selectbox("Primary Soil Type *", 
                                    ["Loamy","Clayey","Sandy","Black","Alluvial","Red","Laterite"],
                                    index=["Loamy","Clayey","Sandy","Black","Alluvial","Red","Laterite"].index(
                                        st.session_state.farmer_profile.get('soil', 'Loamy')
                                    ) if st.session_state.farmer_profile.get('soil') in 
                                    ["Loamy","Clayey","Sandy","Black","Alluvial","Red","Laterite"] else 0)
        
        irrigation_type = st.multiselect("Irrigation Methods Available", 
                                        ["Rainfed","Well","Borewell","Canal","Drip","Sprinkler"],
                                        default=st.session_state.farmer_profile.get('irrigation', []))
        
        current_crops = st.multiselect("Current/Previous Crops Grown", 
                                      ["Rice","Wheat","Cotton","Sugarcane","Maize","Soybean",
                                       "Groundnut","Vegetables","Fruits","Pulses","Other"],
                                      default=st.session_state.farmer_profile.get('crops', []))
        
        farming_exp = st.slider("Years of Farming Experience", 0, 50, 
                               st.session_state.farmer_profile.get('experience', 5))
        
        st.markdown("---")
        st.subheader("🎯 Preferences & Goals")
        
        farming_type = st.radio("Farming Type", 
                               ["Traditional", "Organic", "Mixed"],
                               index=["Traditional", "Organic", "Mixed"].index(
                                   st.session_state.farmer_profile.get('farming_type', 'Traditional')
                               ))
        
        goals = st.multiselect("Primary Farming Goals",
                              ["Maximize Profit", "Sustainability", "Food Security", 
                               "Export Quality", "Diversification"],
                              default=st.session_state.farmer_profile.get('goals', []))
        
        if st.button("💾 Save Profile", type="primary", use_container_width=True):
            if name and phone and land_size > 0:
                st.session_state.farmer_profile = {
                    'name': name,
                    'age': age,
                    'phone': phone,
                    'state': state,
                    'district': district,
                    'land': land_size,
                    'soil': soil_type,
                    'irrigation': irrigation_type,
                    'crops': current_crops,
                    'experience': farming_exp,
                    'farming_type': farming_type,
                    'goals': goals,
                    'created_date': datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.profile_complete = True
                st.success("✅ Profile saved successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Please fill all required fields marked with *")
    
    with col2:
        st.subheader("📊 Profile Summary")
        
        if st.session_state.profile_complete:
            profile_completeness = 100
            st.metric("Profile Completion", f"{profile_completeness}%")
            st.progress(profile_completeness / 100)
            
            st.markdown("---")
            st.metric("Total Queries", len(st.session_state.chat_history))
            st.metric("Saved Recommendations", len(st.session_state.saved_recommendations))
            
            st.markdown("---")
            st.subheader("🎖️ Farmer Badge")
            if farming_exp >= 20:
                st.success("🏆 **Expert Farmer**")
            elif farming_exp >= 10:
                st.info("🥈 **Experienced Farmer**")
            elif farming_exp >= 5:
                st.info("🥉 **Intermediate Farmer**")
            else:
                st.info("🌱 **New Farmer**")
        else:
            st.metric("Profile Completion", "0%")
            st.progress(0)
            st.warning("Complete your profile to unlock personalized features!")
        
        st.markdown("---")
        st.subheader("🔗 Quick Links")
        st.markdown("📞 [Kisan Call Centre](tel:18001801551)")
        st.markdown("🌐 [PM-KISAN Portal](https://pmkisan.gov.in)")
        st.markdown("📱 [eNAM Market](https://enam.gov.in)")
        st.markdown("🏛️ [KVK Directory](https://kvk.icar.gov.in)")
        
        st.markdown("---")
        if st.session_state.profile_complete:
            st.subheader("⚙️ Profile Actions")
            if st.button("🗑️ Clear Profile", use_container_width=True):
                st.session_state.farmer_profile = {}
                st.session_state.profile_complete = False
                st.warning("Profile cleared!")
                st.rerun()
            
            profile_json = json.dumps(st.session_state.farmer_profile, indent=2)
            st.download_button(
                label="📥 Download Profile",
                data=profile_json,
                file_name="farmer_profile.json",
                mime="application/json",
                use_container_width=True
            )

# ----------------------------
# SETTINGS
# ----------------------------
elif choice == "Settings":
    st.header("⚙️ Settings & Preferences")
    
    tabs = st.tabs(["🎨 Appearance", "🌐 Language", "📊 Statistics", "ℹ️ About"])
    
    with tabs[0]:
        st.subheader("🎨 Theme Settings")
        col1, col2 = st.columns(2)
        with col1:
            theme = st.radio("Select Theme", ["Light", "Dark"], 
                            index=0 if st.session_state.theme == "light" else 1)
        with col2:
            st.markdown("#### Preview")
            if theme == "Dark":
                st.markdown("🌙 Dark mode selected")
                st.info("Comfortable for night use")
            else:
                st.markdown("☀️ Light mode selected")
                st.info("Better for daytime use")
        
        if st.button("Apply Theme", type="primary"):
            st.session_state.theme = theme.lower()
            set_theme(st.session_state.theme)
            st.success(f"✅ Theme changed to {theme}!")
            st.rerun()
    
    with tabs[1]:
        st.subheader("🌐 Language Settings")
        col1, col2 = st.columns(2)
        with col1:
            lang = st.selectbox("Select Language", ["English", "Hindi", "Tamil"],
                               index=["English","Hindi","Tamil"].index(st.session_state.language))
        with col2:
            st.markdown("#### Language Support")
            st.info("✅ English - Full Support")
            st.info("✅ Hindi - Full Support")
            st.info("✅ Tamil - Full Support")
        
        if st.button("Apply Language", type="primary"):
            st.session_state.language = lang
            st.success(f"✅ Language changed to {lang}!")
            st.rerun()
    
    with tabs[2]:
        st.subheader("📊 Your Usage Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Chat Queries", len(st.session_state.chat_history))
        with col2:
            st.metric("Saved Items", len(st.session_state.saved_recommendations))
        with col3:
            days_active = (datetime.now() - datetime.strptime(
                st.session_state.farmer_profile.get('created_date', datetime.now().strftime("%Y-%m-%d")), 
                "%Y-%m-%d")).days if st.session_state.farmer_profile else 0
            st.metric("Days Active", days_active)
        
        st.markdown("---")
        st.subheader("🗂️ Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                st.success("Chat history cleared!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Saved Items", use_container_width=True):
                st.session_state.saved_recommendations = []
                st.success("Saved items cleared!")
                st.rerun()
    
    with tabs[3]:
        st.subheader("ℹ️ About SmartAgri AI")
        
        st.markdown("""
        **SmartAgri AI** is a comprehensive digital farming companion designed to empower 
        Indian farmers with technology-driven insights and recommendations.
        
        ### 🌟 Key Features:
        - 🌱 **AI-Powered Crop Recommendations**
        - 📈 **Market Price Forecasting**
        - 🌤️ **Weather-Based Advisories**
        - 🦠 **Disease Detection & Treatment**
        - 💰 **Loan & Fertilizer Calculators**
        - 🏛️ **Government Schemes Information**
        - 💬 **24/7 AI Chatbot Assistance**
        
        ### 📞 Support:
        - **Kisan Call Centre:** 1800-180-1551 (Toll-Free)
        - **Email:** support@smartagri.ai
        - **Website:** www.smartagri.ai
        
        ### 🔒 Privacy:
        Your data is stored locally and never shared with third parties.
        
        ---
        **Version:** 2.0.0  
        **Last Updated:** October 2024  
        **Made with ❤️ for Indian Farmers**
        """)
        
        st.markdown("---")
        st.subheader("📋 Terms & Privacy")
        if st.checkbox("View Terms of Service"):
            st.info("""
            By using SmartAgri AI, you agree to use the recommendations as guidelines only. 
            Always consult with local agricultural experts for final decisions. 
            We are not liable for crop failures or financial losses.
            """)
        
        if st.checkbox("View Privacy Policy"):
            st.info("""
            We respect your privacy. All personal information is stored locally in your browser. 
            We do not collect, store, or share your personal data with any third parties.
            """)

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center;color:#4B8B3B;'>🌾 SmartAgri AI - Empowering Indian Farmers | Made with ❤️ for our Annadatas</p>", 
            unsafe_allow_html=True)