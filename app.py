import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import requests


# ---------------- LOGIN ----------------
def login():
    st.markdown("<h1 style='text-align: center;'>🔐 Travel App Login</h1>", unsafe_allow_html=True)

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "123":
            st.session_state["logged_in"] = True
        else:
            st.error("❌ wrong password")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ---------------- MAIN APP ----------------
st.set_page_config(page_title="AI Travel Planner", layout="wide")

st.markdown("<h1 style='text-align: center; color: green;'>🌍 AI Travel Grouping & Planning System</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📊 Options")
st.sidebar.write("Welcome to Smart Travel App")

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.experimental_rerun()

# Load data
data = pd.read_csv("data.csv")

# Convert interest
mapping = {"beach": 0, "adventure": 1, "temple": 2}
data["interest_num"] = data["interest"].map(mapping)

# Clustering
X = data[["budget", "interest_num", "days"]]
kmeans = KMeans(n_clusters=3)
data["group"] = kmeans.fit_predict(X)

# Recommendation
def get_weather(city):
    api_key = "ad7b4ec6d08590029a18d5374e868345"# 👈 paste your API key here
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url).json()
    
    if response.get("main"):
        temp = response["main"]["temp"]
        return f"{temp}°C"
    else:
        return "Not found"
    
def recommend(interest, budget):
    if interest == "beach":
        return "Goa" if budget < 6000 else "Maldives"
    elif interest == "adventure":
        return "Manali" if budget < 7000 else "Switzerland"
    else:
        return "Tirupati"

data["destination"] = data.apply(lambda x: recommend(x["interest"], x["budget"]), axis=1)

def clean_city(dest):
    return dest.replace("🏖️", "").replace("🏔️", "").replace("🛕", "").strip()
data["weather"] = data["destination"].apply(lambda x: get_weather(clean_city(x)))

st.success("✅ Data loaded with real-time weather!")

st.subheader("🌦️ Weather Information")
st.dataframe(data[["name", "destination", "weather"]])

st.subheader("📊 Group Distribution")
st.bar_chart(data["group"].value_counts())

st.subheader("🔍 Filter by Group")
group_filter = st.selectbox("Select Group", data["group"].unique())

filtered_data = data[data["group"] == group_filter]
st.write(filtered_data)

csv = data.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Data", csv, "travel_data.csv")

# Layout columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("👥 Travelers Data")
    st.dataframe(data, use_container_width=True)

with col2:
    st.subheader("📊 Group Summary")
    st.write(data.groupby("group")["name"].count())

# Add new traveler
st.markdown("---")
st.subheader("➕ Add New Traveler")

name = st.text_input("Name")
budget = st.number_input("Budget", min_value=1000)
interest = st.selectbox("Interest", ["beach", "adventure", "temple"])
days = st.number_input("Days", min_value=1)

if st.button("Add Traveler"):
    st.success(f"✅ {name} added successfully!")