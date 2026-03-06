# AI Trip Planner

An agentic AI travel planner built with LangGraph and Groq. Ask it to plan a trip anywhere in the world — it uses real-time APIs to fetch weather, attractions, restaurants, transportation options, and costs, then returns a full Markdown travel itinerary.

## Architecture

```text
Streamlit UI (app.py)
    │
    │ HTTP (localhost:8000)
    ▼
FastAPI Backend (main.py)  ← started as a background thread by app.py
    │
    ▼
LangGraph ReAct Agent
    │
    ├── Weather Tool        → OpenWeatherMap API
    ├── Place Search Tool   → Google Places API (Tavily fallback)
    ├── Calculator Tool     → Math (hotel cost, daily budget)
    └── Currency Tool       → ExchangeRate-API
```

The FastAPI server is started automatically in a background thread when the Streamlit app launches — no separate terminal needed.

## APIs Required

| API | Free Tier | Link |
| --- | --- | --- |
| Groq | Yes | <https://console.groq.com> |
| OpenWeatherMap | Yes | <https://openweathermap.org/api> |
| Google Places | Yes (limited) | <https://console.cloud.google.com> |
| Tavily | Yes | <https://tavily.com> |
| ExchangeRate-API | Yes | <https://www.exchangerate-api.com> |

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/AI_Trip_Planner.git
cd AI_Trip_Planner
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API keys

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and fill in your keys
```

### 4. Run the app

```bash
streamlit run app.py
```

The FastAPI backend starts automatically in the background. Open <http://localhost:8501> in your browser.

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set the main file to `app.py`
4. Go to **App Settings → Secrets** and paste in your keys from `secrets.toml.example`
5. Deploy

Streamlit Cloud will install `requirements.txt` automatically and the FastAPI backend will start as a background thread alongside the Streamlit UI.

## Project Structure

```text
AI_Trip_Planner/
├── app.py                        # Streamlit UI + FastAPI background thread
├── main.py                       # FastAPI app (POST /query endpoint)
├── agent/
│   └── agentic_workflow.py       # LangGraph ReAct agent
├── tools/
│   ├── weather_info_tool.py      # LangChain tool wrappers for weather
│   ├── place_search_tool.py      # LangChain tool wrappers for places
│   ├── expense_calculator_tool.py
│   └── currency_conversion_tool.py
├── utils/
│   ├── weather_info.py           # OpenWeatherMap API client
│   ├── place_info_search.py      # Google Places + Tavily clients
│   ├── currency_converter.py     # ExchangeRate-API client
│   ├── expense_calculator.py     # Math utilities
│   ├── model_loader.py           # LLM loader (Groq / OpenAI)
│   ├── config_loader.py          # YAML config reader
│   └── save_to_document.py       # Saves output as Markdown file
├── prompt_library/
│   └── prompt.py                 # System prompt for the travel agent
├── config/
│   └── config.yaml               # Model names
├── .streamlit/
│   └── secrets.toml.example      # API key template (copy to secrets.toml)
└── requirements.txt
```

## Example Queries

- `Plan a 5-day trip to Goa for 2 people on a budget`
- `Plan a solo trip to Tokyo for 7 days`
- `Weekend getaway to Coorg from Bangalore`
