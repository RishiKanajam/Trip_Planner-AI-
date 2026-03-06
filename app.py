import os
import threading
import time
from dotenv import load_dotenv
import streamlit as st

# Load .env for local development
load_dotenv()

# Inject Streamlit Cloud secrets as environment variables
for key, value in st.secrets.items():
    os.environ[str(key)] = str(value)

import requests
import datetime
import uvicorn
from main import app as fastapi_app
from utils.weather_info import WeatherForecastTool
from utils.currency_converter import CurrencyConverter

# ── Start FastAPI backend in background thread (once, shared across sessions) ──
@st.cache_resource
def start_fastapi_server():
    def run():
        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="error")
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    time.sleep(1)

start_fastapi_server()

BASE_URL = "http://127.0.0.1:8000"

# ── Page config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Plan My Trip submit button */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 16px;
        padding: 0.6rem 1.2rem;
        width: 100%;
        transition: opacity 0.2s;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        opacity: 0.88;
        border: none;
    }
    /* Sidebar convert button */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
    div[data-testid="stButton"] > button:hover {
        opacity: 0.88;
        border: none;
    }
    /* Query textarea */
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        font-size: 15px;
        border: 1.5px solid #e0e0e0;
    }
    /* Text inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    /* Result meta text */
    .result-meta {
        color: #888;
        font-size: 13px;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────────
WEATHER_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "")
EXCHANGE_API_KEY = os.environ.get("EXCHANGE_RATE_API_KEY", "")

CURRENCIES = [
    "USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "SGD",
    "AED", "THB", "MYR", "CHF", "HKD", "NZD", "SEK", "BRL", "ZAR",
]

# ── Helpers ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_current_weather(city: str):
    tool = WeatherForecastTool(WEATHER_API_KEY)
    return tool.get_current_weather(city)

@st.cache_data(ttl=600)
def fetch_forecast(city: str):
    tool = WeatherForecastTool(WEATHER_API_KEY)
    return tool.get_forecast_weather(city)

def kelvin_to_celsius(k: float) -> float:
    return k - 273.15

def weather_emoji(description: str) -> str:
    d = description.lower()
    if "clear" in d:               return "☀️"
    if "cloud" in d:               return "☁️"
    if "rain" in d:                return "🌧️"
    if "drizzle" in d:             return "🌦️"
    if "thunder" in d:             return "⛈️"
    if "snow" in d:                return "❄️"
    if "mist" in d or "fog" in d:  return "🌫️"
    if "haze" in d:                return "🌤️"
    return "🌡️"

# ── SIDEBAR ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 AI Trip Planner")
    st.caption("LangGraph · Groq · Real-time APIs")
    st.divider()

    # ── Weather Widget ────────────────────────────────────────────────────────────
    st.markdown("### 🌤 Live Weather")
    weather_city = st.text_input(
        "City", placeholder="e.g. Tokyo", key="weather_city", label_visibility="collapsed"
    )

    if weather_city.strip():
        with st.spinner(""):
            data = fetch_current_weather(weather_city.strip())

        if data and "main" in data:
            temp_c    = kelvin_to_celsius(data["main"]["temp"])
            feels_c   = kelvin_to_celsius(data["main"]["feels_like"])
            humidity  = data["main"]["humidity"]
            wind      = data.get("wind", {}).get("speed", 0)
            desc      = data["weather"][0]["description"].title()
            icon_code = data["weather"][0]["icon"]
            city_name = data.get("name", weather_city)
            country   = data.get("sys", {}).get("country", "")
            emoji     = weather_emoji(desc)
            icon_url  = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

            col_ico, col_info = st.columns([1, 2])
            with col_ico:
                st.image(icon_url, width=64)
            with col_info:
                st.markdown(f"**{city_name}, {country}**")
                st.markdown(f"### {temp_c:.1f}°C")
                st.caption(f"{emoji} {desc}")

            m1, m2, m3 = st.columns(3)
            m1.metric("Feels", f"{feels_c:.0f}°C")
            m2.metric("Humidity", f"{humidity}%")
            m3.metric("Wind", f"{wind} m/s")

            with st.expander("Upcoming forecast"):
                fdata = fetch_forecast(weather_city.strip())
                if fdata and "list" in fdata:
                    for item in fdata["list"]:
                        slot_time = item["dt_txt"]
                        slot_temp = item["main"]["temp"]
                        slot_desc = item["weather"][0]["description"].title()
                        slot_emoji = weather_emoji(slot_desc)
                        label = datetime.datetime.strptime(
                            slot_time, "%Y-%m-%d %H:%M:%S"
                        ).strftime("%a %d %b, %I%p")
                        st.markdown(
                            f"`{label}` — **{slot_temp:.1f}°C** {slot_emoji} {slot_desc}"
                        )
                else:
                    st.caption("Forecast unavailable.")
        else:
            st.warning("City not found. Check spelling and try again.")

    st.divider()

    # ── Currency Converter ────────────────────────────────────────────────────────
    st.markdown("### 💱 Currency Converter")

    amount    = st.number_input("Amount", min_value=0.01, value=100.0, step=50.0, label_visibility="collapsed")
    col_f, col_t = st.columns(2)
    from_curr = col_f.selectbox("From", CURRENCIES, index=0)
    to_curr   = col_t.selectbox("To",   CURRENCIES, index=3)  # INR default

    if st.button("Convert", use_container_width=True):
        if not EXCHANGE_API_KEY:
            st.error("Exchange rate API key not set.")
        else:
            try:
                converter = CurrencyConverter(EXCHANGE_API_KEY)
                result = converter.convert(amount, from_curr, to_curr)
                st.success(f"**{amount:,.2f} {from_curr}** → **{result:,.2f} {to_curr}**")
            except Exception as e:
                st.error(f"Conversion failed: {e}")

    st.divider()
    st.caption("Weather cached 10 min · Exchange rates live")

# ── MAIN AREA ────────────────────────────────────────────────────────────────────
st.markdown("# ✈️ Plan Your Perfect Trip")
st.markdown(
    "Describe your trip below — destination, duration, budget, travel style — "
    "and the AI agent will build a complete itinerary with real-time weather, "
    "top attractions, restaurants, transport options, and a full cost breakdown."
)
st.divider()

with st.form("query_form", clear_on_submit=True):
    user_input = st.text_area(
        "Trip query",
        placeholder=(
            "e.g. Plan a 5-day trip to Goa for 2 people in March on a mid-range budget.\n"
            "Include beaches, local food, water sports, and accommodation near the beach."
        ),
        height=120,
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Plan My Trip", use_container_width=True)

with st.expander("Need inspiration? Try these examples"):
    st.markdown("""
- *Plan a 7-day solo trip to Tokyo in April with a budget of $2000*
- *Weekend getaway from Bangalore to Coorg for a couple*
- *Plan a 10-day Europe trip covering Paris, Rome, and Barcelona*
- *Budget backpacking trip across Southeast Asia for 3 weeks*
""")

# ── Result ────────────────────────────────────────────────────────────────────────
if submitted and user_input.strip():
    with st.spinner("Your AI travel agent is researching your trip — this may take a minute..."):
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                json={"question": user_input},
                timeout=180,
            )
        except requests.exceptions.Timeout:
            st.error("The request timed out. The agent took too long — please try again.")
            st.stop()
        except Exception as e:
            st.error(f"Could not reach the backend: {e}")
            st.stop()

    if response.status_code == 200:
        answer = response.json().get("answer", "No answer returned.")
        st.divider()

        col_meta, col_dl = st.columns([3, 1])
        col_meta.markdown(
            f"<p class='result-meta'>Generated on "
            f"{datetime.datetime.now().strftime('%d %b %Y at %H:%M')}</p>",
            unsafe_allow_html=True,
        )
        col_dl.download_button(
            label="Download Plan",
            data=answer,
            file_name=f"trip_plan_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
        )

        st.markdown(answer)
        st.divider()
        st.caption(
            "AI-generated plan. Verify prices, operating hours, and visa/entry "
            "requirements before your trip."
        )
    else:
        st.error("The agent failed to respond. " + response.text)

elif submitted:
    st.warning("Please describe your trip before submitting.")
