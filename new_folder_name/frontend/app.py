
import streamlit as st
import pandas as pd
import joblib
import base64
import altair as alt

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------
st.set_page_config(page_title="Bike Rental Prediction", layout="centered")

# --------------------------------------------------
# BACKGROUND + GLOBAL STYLES
# --------------------------------------------------
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        html, body {{
            height: 100%;
        }}

        body {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        .stApp {{
            max-width: 900px;
            margin: 40px auto;
            padding: 26px 30px;
            border-radius: 22px;
            background: rgba(255,255,255,0.94);
            box-shadow: 0 20px 60px rgba(0,0,0,0.25);
        }}

        h1, h2, h3 {{
            color: #020617 !important;
            font-weight: 800;
        }}

        label {{
            color: #020617 !important;
            font-weight: 600;
        }}

        div[data-baseweb="select"] > div {{
            background-color: #1f2937 !important;
            color: #ffffff !important;
        }}

        div[data-baseweb="select"] span {{
            color: #ffffff !important;
        }}

        ul[role="listbox"] li {{
            background-color: #1f2937 !important;
            color: #ffffff !important;
        }}

        ul[role="listbox"] li:hover {{
            background-color: #374151 !important;
        }}

        .stSlider span {{
            color: #020617 !important;
            font-weight: 600;
        }}

        button {{
            background-color: #f8fafc !important;
            border: 1px solid #cbd5f5 !important;
            border-radius: 14px !important;
            color: #020617 !important;
            font-weight: 600 !important;
        }}

        button:hover {{
            background-color: #e0f2fe !important;
            border-color: #38bdf8 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("wallpaper.png")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = None
if "day_results" not in st.session_state:
    st.session_state.day_results = None
if "hour_results" not in st.session_state:
    st.session_state.hour_results = None

# --------------------------------------------------
# HERO SECTION (ONE-LINE TITLE)
# --------------------------------------------------
st.markdown(
    """
    <style>
    .hero h1 {
        font-size:42px;
        font-weight:900;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        background: linear-gradient(90deg,#020617,#2563eb,#1e40af);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    }
    .hero p {
        color:#334155;
        font-size:17px;
    }
    </style>

    <div class="hero" style="text-align:center; margin:28px 0;">
        <h1> Bike Rental Prediction System</h1>
        <p>Predict daily and hourly bike demand using machine learning</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# REDUCED BG IMAGE (CENTERED)
# --------------------------------------------------
# col1, col2, col3 = st.columns([1, 2, 1])
# with col2:
#     st.image("bg.png", width=250)

import base64

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown(
        """
        <div style="display:flex; justify-content:center; margin-left:12px;">
            <img src="data:image/png;base64,{}" width="250">
        </div>
        """.format(
            base64.b64encode(open("bg.png", "rb").read()).decode()
        ),
        unsafe_allow_html=True
    )

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("📅 Day-wise Prediction", use_container_width=True):
        st.session_state.page = "day"
        st.session_state.hour_results = None

with col2:
    if st.button("⏰ Hour-wise Prediction", use_container_width=True):
        st.session_state.page = "hour"
        st.session_state.day_results = None

st.markdown("<hr style='border:1px solid #cbd5f5; margin:32px 0;'>",
            unsafe_allow_html=True)

# --------------------------------------------------
# LOAD MODELS
# --------------------------------------------------
day_model = joblib.load("day_model.pkl")
hour_model = joblib.load("hour_model.pkl")

# --------------------------------------------------
# MAPS
# --------------------------------------------------
season_map = {"Spring":1,"Summer":2,"Fall":3,"Winter":4}
weekday_map = {
    "Sunday":0,"Monday":1,"Tuesday":2,
    "Wednesday":3,"Thursday":4,"Friday":5,"Saturday":6
}
weather_map = {
    "Clear / Few clouds":1,
    "Mist / Cloudy":2,
    "Light Rain / Snow":3,
    "Heavy Rain / Thunderstorm":4
}
binary_map = {"No":0,"Yes":1}
months = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

DAY_LIST = list(weekday_map.keys())

def rotate_days(start_day):
    idx = DAY_LIST.index(start_day)
    return DAY_LIST[idx:] + DAY_LIST[:idx]

# ==================================================
# DAY PAGE
# ==================================================
if st.session_state.page == "day":

    st.header("📅 Daily Bike Rental Prediction")

    season = season_map[st.selectbox("Season", season_map)]
    month = months.index(st.selectbox("Month", months)) + 1
    holiday = binary_map[st.selectbox("Holiday", binary_map)]
    start_day = st.selectbox("Starting Day", weekday_map)
    weekday_num = weekday_map[start_day]
    workingday = binary_map[st.selectbox("Working Day", binary_map)]
    weather = weather_map[st.selectbox("Weather Condition", weather_map)]

    temp = st.slider("Temperature (0–1)", 0.0, 1.0)
    atemp = st.slider("Feels-like Temperature (0–1)", 0.0, 1.0)
    hum = st.slider("Humidity (0–1)", 0.0, 1.0)
    wind = st.slider("Windspeed (0–1)", 0.0, 1.0)

    if st.button("Predict Weekly Demand"):
        results = []
        for i in range(7):
            d = (weekday_num + i) % 7
            df = pd.DataFrame([{
                "season": season,
                "mnth": month,
                "holiday": holiday,
                "weekday": d,
                "workingday": workingday,
                "weathersit": weather,
                "temp": temp,
                "atemp": atemp,
                "hum": hum,
                "windspeed": wind
            }])
            pred = int(day_model.predict(df)[0])
            results.append({"Day": DAY_LIST[d], "Count": pred})

        st.session_state.day_results = results

    if st.session_state.day_results:
        dfw = pd.DataFrame(st.session_state.day_results)
        ordered_days = rotate_days(start_day)

        st.altair_chart(
            (
                alt.Chart(dfw)
                .mark_bar(
                    color="#2563eb",
                    cornerRadiusTopLeft=6,
                    cornerRadiusTopRight=6,
                    tooltip=None
                )
                .encode(
                    x=alt.X("Day:N", sort=ordered_days),
                    y=alt.Y("Count:Q", scale=alt.Scale(domain=[0, dfw["Count"].max()*1.25]))
                )
                +
                alt.Chart(dfw)
                .mark_text(
                    dy=-8,
                    color="#E4E6F0",
                    fontSize=13,
                    fontWeight="bold"
                )
                .encode(
                    x=alt.X("Day:N", sort=ordered_days),
                    y="Count:Q",
                    text="Count:Q"
                )
            )
            .properties(height=380),
            use_container_width=True
        )

# ==================================================
# HOURLY PAGE
# ==================================================
if st.session_state.page == "hour":

    st.header("⏰ Hourly Bike Rental Prediction")

    season = season_map[st.selectbox("Season", season_map)]
    month = months.index(st.selectbox("Month", months)) + 1
    hour = st.slider("Hour (0–23)", 0, 23)
    holiday = binary_map[st.selectbox("Holiday", binary_map)]
    weekday = weekday_map[st.selectbox("Weekday", weekday_map)]
    workingday = binary_map[st.selectbox("Working Day", binary_map)]
    weather = weather_map[st.selectbox("Weather Condition", weather_map)]

    temp = st.slider("Temperature (0–1)", 0.0, 1.0)
    atemp = st.slider("Feels-like Temperature (0–1)", 0.0, 1.0)
    hum = st.slider("Humidity (0–1)", 0.0, 1.0)
    wind = st.slider("Windspeed (0–1)", 0.0, 1.0)

    if st.button("Predict Next 5 Hours"):
        results = []
        for i in range(5):
            h = (hour + i) % 24
            df = pd.DataFrame([{
                "season": season,
                "mnth": month,
                "hr": h,
                "holiday": holiday,
                "weekday": weekday,
                "workingday": workingday,
                "weathersit": weather,
                "temp": temp,
                "atemp": atemp,
                "hum": hum,
                "windspeed": wind
            }])
            pred = int(hour_model.predict(df)[0])
            results.append({"Hour": f"{h}:00", "Count": pred})

        st.session_state.hour_results = results

    if st.session_state.hour_results:
        dfh = pd.DataFrame(st.session_state.hour_results)

        st.altair_chart(
            (
                alt.Chart(dfh)
                .mark_bar(
                    color="#1e40af",
                    cornerRadiusTopLeft=6,
                    cornerRadiusTopRight=6,
                    tooltip=None
                )
                .encode(
                    x="Hour:N",
                    y=alt.Y("Count:Q", scale=alt.Scale(domain=[0, dfh["Count"].max()*1.25]))
                )
                +
                alt.Chart(dfh)
                .mark_text(
                    dy=-8,
                    color="#E4E6F0",
                    fontSize=13,
                    fontWeight="bold"
                )
                .encode(
                    x="Hour:N",
                    y="Count:Q",
                    text="Count:Q"
                )
            )
            .properties(height=380),
            use_container_width=True
        )
