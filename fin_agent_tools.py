import streamlit as st
from crewai.tools import BaseTool
import yfinance as yf
from datetime import datetime
#from crewai.utilities import TaskOutput
from typing import Optional, Tuple, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd



# Crew Ai Tool - YFinanceDataTool
class StockDisplayTool:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.info, self.stock = self._get_stock_info()
        self.hist = self._get_stock_history()
        self.nasdaq_hist = self._get_nasdaq_history()

    def _get_stock_info(self) -> Tuple[Dict[str, Any], Any]:
        stock = yf.Ticker(self.ticker)
        return stock.info, stock

    def _get_stock_history(self) -> pd.DataFrame:
        return self.stock.history(period="5y")

    def _get_nasdaq_history(self) -> pd.DataFrame:
        nasdaq = yf.Ticker("^IXIC")
        return nasdaq.history(period="5y")

    def display_header(self):
        st.subheader(
            f'{self.info.get("longName", "N/A")} 🏷️ :green-background[{self.ticker}] Overview',
            divider='grey'
        )

    def display_metrics(self):
        current_price = self.info.get('currentPrice', 'N/A')
        previous_close = self.info.get('previousClose', 'N/A')

        if current_price != 'N/A' and previous_close != 'N/A':
            day_change = current_price - previous_close
            day_change_percent = (day_change / previous_close) * 100

            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            col0, col1, col2, col3 = st.columns([1, 2, 2, 3])
            
            with col0:
                st.image(f"https://logos.stockanalysis.com/{self.ticker.lower()}.svg", width=60)
            with col1:
                st.metric(f"📈 {self.ticker}", f"$ {current_price:.2f}", f"{day_change_percent:.2f} %")
            with col2:
                st.metric(f"📈 Market Cap", f"{self.info.get('marketCap', 'N/A') / 1e9:.2f} B$", f"P/S: {self.info.get('priceToSalesTrailing12Months', 'N/A'):.2f}")
            with col3:
                st.write(f"**Sector:** `{self.info.get('sector', 'N/A')}`")
                st.write(f"**Industry:** `{self.info.get('industry', 'N/A')}`")
            st.markdown('</div>', unsafe_allow_html=True)

    def display_company_description(self):
        with st.expander(f"🏢 {self.ticker} Company Description"):
            st.write(self.info.get('longBusinessSummary', 'N/A'))

    def display_chart(self):
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add price line
        fig.add_trace(
            go.Scatter(x=self.hist.index, y=self.hist['Close'], name='Close', line=dict(color='#00C4B4')),
            secondary_y=False
        )

        # Add volume bars
        fig.add_trace(
            go.Bar(
                x=self.hist.index,
                y=self.hist['Volume'],
                name='Volume',
                marker_color='rgba(128, 128, 128, 0.3)',
                width=0.1
            ),
            secondary_y=True
        )

        # Add moving average
        self.hist['MA100'] = self.hist['Close'].rolling(window=100).mean()
        fig.add_trace(
            go.Scatter(x=self.hist.index, y=self.hist['MA100'], name='MA100', line=dict(color='#FF6B6B')),
            secondary_y=False
        )

        # Update layout
        fig.update_layout(
            title=f'📉 {self.ticker} Price Chart',
            xaxis_title='Date',
            yaxis_title='Price',
            plot_bgcolor='#2A3142',
            paper_bgcolor='#2A3142',
            font=dict(color='#E0E7FF'),
            title_font=dict(size=20),
        )
        fig.update_yaxes(
            title_text="Volume",
            secondary_y=True,
            range=[0, self.hist['Volume'].max() * 5],
            gridcolor='rgba(128, 128, 128, 0.2)'
        )
        fig.update_xaxes(gridcolor='rgba(128, 128, 128, 0.2)')

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def display_all(self):
        self.display_header()
        self.display_metrics()
        self.display_company_description()
        self.display_chart()



# Crew Ai Tool - YFinanceDataTool
class YFinanceDataTool(BaseTool):
    name: str = "Stock Data Collector"
    description: str = """
    Useful to collect financial data for a given stock ticker using yfinance.
    arg : ticker (str)
    """

    def _run(self, ticker: str) -> str:
      tick = yf.Ticker(ticker)
      info = tick.info
      current_date = datetime.now().strftime("%Y-%m-%d")
      
      text = f"""
      ---- {info.get('shortName', 'N/A')} ({ticker}) Financial Sheet ----

      ** Date : {current_date}

      # Company Overview:
      Symbol: {info.get('symbol', 'N/A')}
      Company Name: {info.get('shortName', 'N/A')}
      Current Price: ${info.get('currentPrice', 'N/A')}
      Market Cap: ${info.get('marketCap', 'N/A')}
      Industry: {info.get('industry', 'N/A')}
      Sector: {info.get('sector', 'N/A')}
      Country: {info.get('country', 'N/A')}
      Employees: {info.get('fullTimeEmployees', 'N/A')}

      # Financial Ratios:
      Trailing P/E: {info.get('trailingPE', 'N/A')}
      Forward P/E: {info.get('forwardPE', 'N/A')}
      Price to Sales (TTM): {info.get('priceToSalesTrailing12Months', 'N/A')}
      Enterprise/Revenue: {info.get('enterpriseToRevenue', 'N/A')}
      Enterprise/EBITDA: {info.get('enterpriseToEbitda', 'N/A')}
      Return on Assets: {info.get('returnOnAssets', 'N/A')}
      Return on Equity: {info.get('returnOnEquity', 'N/A')}
      Price to Book: {info.get('priceToBook', 'N/A')}

      # Company Valuation:
      Total Revenue: ${info.get('totalRevenue', 'N/A')}
      Net Income: ${info.get('netIncomeToCommon', 'N/A')}``
      Revenue Per Share: ${info.get('revenuePerShare', 'N/A')}
      Total Cash: ${info.get('totalCash', 'N/A')}
      Free cash flow: ${info.get('freeCashflow', 'N/A')}
      Enterprise Value: ${info.get('enterpriseValue', 'N/A')}
      Book Value: {info.get('bookValue', 'N/A')}

      # Financial Profitabilty and Growth :
      Quarterly Revenue Growth: {info.get('revenueGrowth', 'N/A')}
      Revenue Growth: {info.get('revenueGrowth', 'N/A')}
      Earnings Growth: {info.get('earningsGrowth', 'N/A')}
      Gross Margins: {info.get('grossMargins', 'N/A')}
      Operating Margins: {info.get('operatingMargins', 'N/A')}
      EBITDA Margins: {info.get('ebitdaMargins', 'N/A')}
      Profit Margins: {info.get('profitMargins', 'N/A')}

      # Market Price Action :
      Price: ${info.get('currentPrice', 'N/A')}
      Year Range: ${info.get('fiftyTwoWeekLow', 'N/A')} - ${info.get('fiftyTwoWeekHigh', 'N/A')}
      Beta: {info.get('beta', 'N/A')}
      Volume: {info.get('volume', 'N/A')}
      Average Volume: {info.get('averageVolume', 'N/A')}

      # Dividend Information:
      Dividend Rate: ${info.get('dividendRate', 'N/A')}
      Dividend Yield: {info.get('dividendYield', 'N/A')}
      Payout Ratio: {info.get('payoutRatio', 'N/A')}
      5Y Avg Dividend Yield: {info.get('fiveYearAvgDividendYield', 'N/A')}

      # Debt Overview:
      Total Debt: ${info.get('totalDebt', 'N/A')}
      Quick Ratio: {info.get('quickRatio', 'N/A')}
      Current Ratio: {info.get('currentRatio', 'N/A')}
      Debt to Equity: {info.get('debtToEquity', 'N/A')}

      # Analyst Recommendations:
      Target Price Range (low - high): ${info.get('targetLowPrice', 'N/A')} - ${info.get('targetHighPrice', 'N/A')}
      Mean Target: ${info.get('targetMeanPrice', 'N/A')}
      Recommendation: {info.get('recommendationKey', 'N/A')}
      Number of Analysts: {info.get('numberOfAnalystOpinions', 'N/A')}

      # Risk :
      Audit Risk: {info.get('auditRisk', 'N/A')}
      Board Risk: {info.get('boardRisk', 'N/A')}
      Compensation Risk: {info.get('compensationRisk', 'N/A')}
      DhareHolder Rights Risk: {info.get('shareHolderRightsRisk', 'N/A')}
      Overall Risk: {info.get('overallRisk', 'N/A')}

      # Short Interest:
      Float Shares: {info.get('floatShares', 'N/A')}
      Shares Outstanding: {info.get('sharesOutstanding', 'N/A')}
      Shares Short: {info.get('sharesShort', 'N/A')}
      Short Ratio: {info.get('shortRatio', 'N/A')}
      Short % of Float: {info.get('shortPercentOfFloat', 'N/A')}
      Institutional Holdings: {info.get('heldPercentInstitutions', 'N/A')}
      """
      return text
