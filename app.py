import streamlit as st
import yfinance as yf
import plotly.express as px
from fin_agent_tools import StockDisplayTool, YFinanceDataTool
from prompts import REPORTER_TASK_PROMPT, ReportOutput
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from datetime import datetime
from typing import Optional
import streamlit.components.v1 as components

# Streamlit app setup
st.set_page_config(
    page_title="StockIntel Crew",
    page_icon="🖥️",
    layout="wide"
)

# Custom CSS for styling
custom_css = """
<style>
/* Set the background for the entire app */
.stApp {
    position: relative;
    min-height: 100vh;
    background: #05000a; /* Fallback color */
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start; /* Align content to the top */
}
/* Ensure the app content is above the background */
.stApp > * {
    position: relative;
    z-index: 1;
}
/* Style the main header to ensure it stays at the top */
h1 {
    color: #E0E7FF;
    font-weight: 600;
    margin-top: 0; /* Remove default margin */
    padding-top: 20px; /* Add some padding for spacing */
    text-align: center; /* Center the header horizontally */
}
/* General app styling */
body {
    font-family: 'Inter', sans-serif;
}
/* Card styling for sections */
.stCard {
    background-color: #2A3142;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    margin-bottom: 20px;
    transition: transform 0.2s ease-in-out;
}
.stCard:hover {
    transform: translateY(-5px);
}
/* Header styling */
h2, h3 {
    color: #E0E7FF;
    font-weight: 600;
}
h2 {
    border-bottom: 2px solid #059CE2;
    padding-bottom: 8px;
}
/* Input and button styling */
.stTextInput > div > div > input {
    background-color: #3A4256;
    color: #E0E7FF;
    border: 1px solid #059CE2;
    border-radius: 8px;
    padding: 10px;
}
.stMultiSelect > div > div > div {
    background-color: #3A4256;
    color: #E0E7FF;
    border: 1px solid #059CE2;
    border-radius: 8px;
}
.stButton > button {
    background: linear-gradient(90deg, #059CE2 0%, #00A1A1 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 500;
    transition: background 0.3s ease;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #00A1A1 0%, #008080 100%);
}
/* Metric styling */
.stMetric {
    background-color: #3A4256;
    border-radius: 8px;
    padding: 10px;
    margin: 5px 0;
}
.stMetric label {
    color: #A3BFFA;
    font-size: 14px;
}
.stMetric .stMetricValue {
    color: #E0E7FF;
    font-size: 20px;
    font-weight: 600;
}
/* Expander styling */
.stExpander {
    background-color: #2A3142;
    border-radius: 8px;
    border: 1px solid #3A4256;
}
.stExpander summary {
    color: #00C4B4;
    font-weight: 500;
}
/* Divider styling */
hr {
    border: 1px solid #3A4256;
}
/* Caption styling */
.stCaption {
    color: #A3BFFA;
    font-style: italic;
}
</style>
"""

# Particles.js background
particles_js = """
<div id="particles-js"></div>
<style>
#particles-js {
    position: fixed;
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    z-index: -1; /* Send the animation to the back */
    background: #05000a; /* Fallback background color */
}
#particles-js canvas {
    position: absolute;
    top: 0;
    left: 0;
    z-index: -1;
}
.stApp {
    position: relative;
    z-index: 1;
    background: transparent !important; /* Ensure Streamlit app background is transparent */
}
/* Add a semi-transparent overlay to improve text readability */
.stApp::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5); /* Adjust opacity as needed */
    z-index: -1;
}
</style>
<script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
<script>
if (typeof particlesJS === 'undefined') {
    console.error("particles.js failed to load!");
} else {
    console.log("particles.js loaded successfully!");
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 300,
          "density": {
            "enable": true,
            "value_area": 800
          }
        },
        "color": {
          "value": "#ffffff"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 0,
            "color": "#000000"
          },
          "polygon": {
            "nb_sides": 5
          },
          "image": {
            "src": "img/github.svg",
            "width": 100,
            "height": 100
          }
        },
        "opacity": {
          "value": 0.5,
          "random": false,
          "anim": {
            "enable": false,
            "speed": 1,
            "opacity_min": 0.1,
            "sync": false
          }
        },
        "size": {
          "value": 3,
          "random": true,
          "anim": {
            "enable": false,
            "speed": 40,
            "size_min": 0.1,
            "sync": false
          }
        },
        "line_linked": {
          "enable": true,
          "distance": 100,
          "color": "#ffffff",
          "opacity": 0.22,
          "width": 1
        },
        "move": {
          "enable": true,
          "speed": 2,
          "direction": "none",
          "random": false,
          "straight": false,
          "out_mode": "out",
          "bounce": true,
          "attract": {
            "enable": false,
            "rotateX": 600,
            "rotateY": 1200
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": true,
            "mode": "grab"
          },
          "onclick": {
            "enable": true,
            "mode": "repulse"
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 100,
            "line_linked": {
              "opacity": 1
            }
          },
          "bubble": {
            "distance": 400,
            "size": 2,
            "duration": 2,
            "opacity": 0.5,
            "speed": 1
          },
          "repulse": {
            "distance": 200,
            "duration": 0.4
          },
          "push": {
            "particles_nb": 2
          },
          "remove": {
            "particles_nb": 3
          }
        }
      },
      "retina_detect": true
    });
}
</script>
"""

# Initialize session state for animation
if "show_animation" not in st.session_state:
    st.session_state.show_animation = True

# Apply custom CSS and background
st.markdown(custom_css, unsafe_allow_html=True)

# Streamlit app setup
st.title("🖥️ *StockIntel-Crew*")

# Retrieve API key from secrets
GROQ_API_KEY = st.secrets["GROQ_API"]

# Define LLMs
llm = LLM(
    api_key=GROQ_API_KEY,
    model="groq/gemma2-9b-it",
    temperature=0.1,
)

llm_groq_mixtral = LLM(
    api_key=GROQ_API_KEY,
    model="groq/mixtral-8x7b-32768",
    temperature=0.2,
    max_tokens=4000,
    response_format={"type": "json"},
)

# Tool
yfinance_tool = YFinanceDataTool()

# Agents
collector = Agent(
    role='Financial Data Collector',
    goal='Collect comprehensive financial data for the given stock ticker',
    backstory='A financial data specialist with expertise in gathering market information.',
    llm=llm,
    tools=[yfinance_tool],
    allow_delegation=False,
    max_iter=1,
    verbose=True
)

reporter = Agent(
    role='Financial Analyst',
    goal='Analyze financial data and create detailed financial reports',
    backstory='An experienced financial analyst specializing in stock market analysis and financial reporting.',
    llm=llm,
    allow_delegation=False,
    max_iter=3,
    verbose=True
)

# Callbacks
def task_callback(output):
    if output.raw:
        st.caption(f"☑️ {output.summary}")
    else:
        st.write("No Output")

# Tasks
collect_data = Task(
    description="Collect financial data for the specified stock {ticker} using yfinance.",
    expected_output='A comprehensive dictionary containing all available financial data for the stock.',
    agent=collector,
    callback=task_callback
)

analyze_data = Task(
    description="""
    Analyze the collected {ticker} financial data and create a detailed financial report including:
    1. Company Overview
    2. Financial Ratios Analysis
    3. Market Performance
    4. Risk Assessment
    5. Investment Recommendation
    Use the data provided by the collector to support your analysis.
    """,
    expected_output=REPORTER_TASK_PROMPT,
    agent=reporter,
    context=[collect_data],
    callback=task_callback
)

# Crew
@st.cache_resource
def create_crew():
    crew = Crew(
        agents=[collector, reporter],
        tasks=[collect_data, analyze_data],
        verbose=True
    )
    return crew

# Input section with card styling
with st.container():
    ticker = st.text_input("Enter stock ticker:", "IONQ", help="Enter a valid stock ticker (e.g., AAPL, TSLA)")
    if st.button("Analyze Stock, Generate Financial Report", use_container_width=True):
        with st.spinner(f"Generating :orange[{ticker}] Financial Report..."):
            crew = create_crew()
            stock_display = StockDisplayTool(ticker)
            result = crew.kickoff(inputs={'ticker': ticker})
            st.divider()
            stock_display.display_all()
            st.divider()
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()
            st.caption("**AI-generated Report** | NFA, Please DYOR before investing.")
if st.session_state.show_animation:
    components.html(particles_js, height=370, scrolling=False)