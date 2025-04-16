# Stockintel-crew

The stockintel crew is a Streamlit-based application crafted to streamline comprehensive stock market analysis. It harnesses advanced large language models (LLMs) and tools to efficiently collect, evaluate, and present financial data.

Features

Financial Data Aggregation: Employs sophisticated agents to retrieve data for selected stock tickers.
In-Depth Analytical Reports: Produces detailed financial insights through AI-powered analysis.
User-Friendly Interface: Offers an intuitive, Streamlit-driven platform for seamless interaction.
Requirements

Python 3.8 or higher
Streamlit
yfinance
crewai
A valid API key for Groq models
How It Operates

Agent-Driven Framework: The app utilizes two specialized agents:
Collector Agent: Acquires stock data via yfinance and complementary tools.
Reporter Agent: Evaluates the gathered data to deliver actionable insights.
LLM Integration: Leverages Groq’s gemma2-9b-it and mixtral-8x7b-32768 models for advanced natural language processing and response generation.
Interactive Experience: Enables users to input stock tickers and access real-time data and analytical results through a dynamic display.
